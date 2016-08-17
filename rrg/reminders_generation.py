from datetime import datetime as dt
import hashlib
from sqlalchemy import and_

from s3_mysql_backup import YMD_FORMAT

from rrg.models import Invoice
from rrg.models import Contract
from rrg.models import Client
from rrg.models import Employee
from rrg.models import Iitem
from rrg.models import Citem
from rrg.reminders import weeks_between_dates
from rrg.reminders import biweeks_between_dates
from rrg.reminders import semimonths_between_dates
from rrg.reminders import months_between_dates
from rrg.helpers import date_to_datetime
from rrg.queries import contracts_per_period

"""
this module differs from reminders in that it depends on models
"""


def reminder_hash(contract, start, end):
    """
    from the point of view of contract generate hash for contract-pay-period
    :param contract:
    :param start:
    :param end:
    :return:
    """

    return hashlib.sha224('%s %s %s' % (
        contract.id, dt.strftime(start, YMD_FORMAT), dt.strftime(end, YMD_FORMAT))).hexdigest()


def timecard_hash(timecard):
    return hashlib.sha224('%s %s %s' % (
        timecard.contract.id, dt.strftime(timecard.period_start, YMD_FORMAT),
        dt.strftime(timecard.period_end, YMD_FORMAT))).hexdigest()


def timecards(session, args):
    """
    returns set of timecard hashs of contract.id+startdate+enddate
    :return:
    """
    with session.no_autoflush:
        return session.query(Invoice, Contract, Employee, Client).join(Contract).join(Employee).join(Client).filter(
            and_(Client.active == 1, Contract.active == 1, Employee.active == 1)).all()


def reminders_set(session, args):

    args.period = 'week'
    contracts_w = contracts_per_period(session, args)

    args.period = 'biweek'
    contracts_b = contracts_per_period(session, args)

    args.period = 'semimonth'
    contracts_s = contracts_per_period(session, args)

    args.period = 'month'
    contracts_m = contracts_per_period(session, args)
    #
    reminders_set = set()
    for c, cl, em in contracts_w:
        for ws, we in weeks_between_dates(date_to_datetime(c.startdate), args.payroll_run_date):
            reminders_set.add(reminder_hash(c, ws, we))
    for c, cl, em in contracts_b:
        for ws, we in biweeks_between_dates(date_to_datetime(c.startdate), args.payroll_run_date):
            reminders_set.add(reminder_hash(c, ws, we))
    for c, cl, em in contracts_s:
        for ws, we in semimonths_between_dates(date_to_datetime(c.startdate), args.payroll_run_date):
            reminders_set.add(reminder_hash(c, ws, we))
    for c, cl, em in contracts_m:
        for ws, we in months_between_dates(date_to_datetime(c.startdate), args.payroll_run_date):
            reminders_set.add(reminder_hash(c, ws, we))
    return reminders_set


def reminders(session, reminder_period_start, payroll_run_date, t_set, args):
    #
    reminders = []
    for c, cl, em in contracts_per_period(session, args):
        if args.period == 'week':
            for ws, we in weeks_between_dates(reminder_period_start, payroll_run_date):
                if reminder_hash(c, ws, we) not in t_set:
                    reminders.append((c, ws, we))
        elif args.period == 'biweek':
            for ws, we in biweeks_between_dates(date_to_datetime(c.startdate), payroll_run_date):
                if reminder_hash(c, ws, we) not in t_set:
                    reminders.append((c, ws, we))
        elif args.period == 'semimonth':
            for ws, we in semimonths_between_dates(date_to_datetime(c.startdate), payroll_run_date):
                if reminder_hash(c, ws, we) not in t_set:
                    reminders.append((c, ws, we))
        else:
            for ws, we in months_between_dates(date_to_datetime(c.startdate), payroll_run_date):
                if reminder_hash(c, ws, we) not in t_set:
                    reminders.append((c, ws, we))

    return reminders


def timecards_set(session, args):

    timecards_set = set()
    for t in timecards(session, args):

        timecards_set.add(timecard_hash(t[0]))
    return timecards_set


def rebuild_empty_invoice_commissions(session, inv):
    """
    this should be used to build the sql.  from invoice items from invoices for period with no comm items
    This should be used once and thrown away, because of a bug, invoice items do not have parent ids.
    this will cause redundancies, if run multiple times
    :fixme
    :param session:
    :param inv:
    :return:
    """

    for citem in inv.contract.contract_items:
        new_iitem = Iitem(invoice_id=inv.id, description=citem.description, cost=citem.cost, amount=citem.amt)
        session.add(new_iitem)
        for comm_item in citem.comm_items:
            new_sales_comm_item = Citem(
                invoices_item_id=new_iitem.id, employee_id=comm_item.employee_id,
                percent=comm_item.percent, description=new_iitem.description)
            session.add(new_sales_comm_item)


def create_invoice_for_period(session, contract, period_start, period_end):
    new_inv = Invoice(contract_id=contract.id, period_start=period_start, period_end=period_end)
    session.add(new_inv)
    for citem in contract.contract_items:
        new_iitem = Iitem(invoice_id=new_inv.id, description=citem.description, cost=citem.cost, amount=citem.amt)
        session.add(new_iitem)
        for comm_item in citem.comm_items:
            new_sales_comm_item = Citem(
                invoices_item_id=new_iitem.id, employee_id=comm_item.employee_id,
                percent=comm_item.percent, description=new_iitem.description)
            session.add(new_sales_comm_item)
