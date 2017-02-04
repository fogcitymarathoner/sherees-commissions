from datetime import datetime as dt
import hashlib
import logging
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

logging.basicConfig(filename='testing.log', level=logging.DEBUG)
logger = logging.getLogger('test')

logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

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
        contract.id, dt.strftime(start, YMD_FORMAT),
        dt.strftime(end, YMD_FORMAT))).hexdigest()


def timecard_hash(timecard):
    return hashlib.sha224('%s %s %s' % (
        timecard.contract.id, dt.strftime(timecard.period_start, YMD_FORMAT),
        dt.strftime(timecard.period_end, YMD_FORMAT))).hexdigest()


def timecards(session, args):
    """
    returns set of timecard hashs of contract.id+startdate+enddate
    timecard not used
    :return:
    """
    with session.no_autoflush:
        return session.query(Invoice, Contract, Employee, Client).join(
            Contract).join(Employee).join(Client).filter(
            and_(Client.active == 1, Contract.active == 1,
                 Employee.active == 1)).all()


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
        for ws, we in weeks_between_dates(date_to_datetime(c.startdate),
                                          args.payroll_run_date):
            reminders_set.add(reminder_hash(c, ws, we))
    for c, cl, em in contracts_b:
        for ws, we in biweeks_between_dates(date_to_datetime(c.startdate),
                                            args.payroll_run_date):
            reminders_set.add(reminder_hash(c, ws, we))
    for c, cl, em in contracts_s:
        for ws, we in semimonths_between_dates(date_to_datetime(c.startdate),
                                               args.payroll_run_date):
            reminders_set.add(reminder_hash(c, ws, we))
    for c, cl, em in contracts_m:
        for ws, we in months_between_dates(date_to_datetime(c.startdate),
                                           args.payroll_run_date):
            reminders_set.add(reminder_hash(c, ws, we))
    return reminders_set


def reminders(session, reminder_period_start, payroll_run_date, t_set, args):
    # generate list of reminders in a period for a period type [week, biweek, semimonth, month]

    reminders = []
    for c, cl, em in contracts_per_period(session, args):
        if args.period == 'week':
            for ws, we in weeks_between_dates(reminder_period_start,
                                              payroll_run_date):
                if reminder_hash(c, ws, we) not in t_set:
                    reminders.append((c, ws, we))
        elif args.period == 'biweek':
            for ws, we in biweeks_between_dates(date_to_datetime(c.startdate),
                                                payroll_run_date):
                if reminder_hash(c, ws, we) not in t_set:
                    reminders.append((c, ws, we))
        elif args.period == 'semimonth':
            for ws, we in semimonths_between_dates(
                    date_to_datetime(c.startdate), payroll_run_date):
                if reminder_hash(c, ws, we) not in t_set:
                    reminders.append((c, ws, we))
        else:
            for ws, we in months_between_dates(date_to_datetime(c.startdate),
                                               payroll_run_date):
                if reminder_hash(c, ws, we) not in t_set:
                    reminders.append((c, ws, we))

    return reminders


def reminder_to_timecard(session, reminder_period_start, payroll_run_date, t_set,
                    args):
    """
    A new invoice is a timecard if voided False and timecard true
    """
    # create voided invoice for args.number'th reminder from reminders

    reminders_tbs = reminders(session, reminder_period_start, payroll_run_date,
                              t_set, args)

    contract, start, end = reminders_tbs[args.number - 1]
    new_inv = create_invoice_for_period(session, contract, start, end)
    new_inv.voided = False
    new_inv.mock = False
    new_inv.timecard = True

def forget_reminder(session, reminder_period_start, payroll_run_date, t_set,
                    args):
    # create voided invoice for args.number'th reminder from reminders

    reminders_tbs = reminders(session, reminder_period_start, payroll_run_date,
                              t_set, args)

    contract, start, end = reminders_tbs[args.number - 1]
    new_inv = create_invoice_for_period(session, contract, start, end)
    new_inv.voided = True

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

    for iitem in inv.invoice_items:
        logger.debug(iitem)
        ci = Citem(
            invoices_item_id=iitem.id, employee_id=1025,
            created_date=dt.now(), modified_date=dt.now(),
            created_user_id=2, modified_user_id=2,
            percent=61.5, date=inv.date, description=iitem.description,
            amount=.615 * (
                iitem.quantity * (iitem.amount - iitem.cost) -
                iitem.quantity * (iitem.amount - iitem.cost) * .1))

        session.add(ci)

        ci = Citem(
            invoices_item_id=iitem.id, employee_id=1479,
            created_date=dt.now(), modified_date=dt.now(),
            created_user_id=2, modified_user_id=2,
            percent=38.5, date=inv.date, description=iitem.description,
            amount=.385 * (
                iitem.quantity * (
                iitem.amount - iitem.cost) - iitem.quantity * (
                    iitem.amount - iitem.cost) * .1))

        session.add(ci)


def create_invoice_for_period(session, contract, period_start, period_end, date=None):
    if not date:
        date = dt.now()
    new_inv = Invoice(contract_id=contract.id, period_start=period_start,
                      period_end=period_end, date=date,
                      employerexpenserate=.10, terms=contract.terms, 
                      posted=False, prcleared=False, timecard=False,
                      cleared=False, timecard_receipt_sent=False,
                      message='Thank you for your business!', amount=0,
                      voided=False)
    session.add(new_inv)
    session.flush()
    for citem in contract.contract_items:
        new_iitem = Iitem(invoice_id=new_inv.id, description=citem.description,
                          quantity=0.0, cleared=False,
                          cost=citem.cost, amount=citem.amt)
        session.add(new_iitem)
        session.flush()
        for comm_item in citem.contract_comm_items:
            new_sales_comm_item = Citem(invoices_item_id=new_iitem.id,
                                        employee_id=comm_item.employee_id,
                                        percent=comm_item.percent,
                                        cleared=False, amount=0,
                                        description=new_iitem.description)
            session.add(new_sales_comm_item)
    return new_inv
