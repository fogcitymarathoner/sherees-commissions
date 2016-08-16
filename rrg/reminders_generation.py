from datetime import datetime as dt
import hashlib
from sqlalchemy import and_

from s3_mysql_backup import YMD_FORMAT

from rrg.models import Invoice
from rrg.models import Contract
from rrg.models import Client
from rrg.models import Employee
from rrg.reminders import weeks_between_dates
from rrg.reminders import biweeks_between_dates
from rrg.reminders import semimonths_between_dates
from rrg.reminders import months_between_dates
from rrg.helpers import date_to_datetime
from rrg.queries import contracts_per_period
from rrg.models import session_maker

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


def timecards():
    """
    returns set of timecard hashs of contract.id+startdate+enddate
    :return:
    """

    with session.no_autoflush:
        return session.query(Invoice, Contract, Employee, Client).join(Contract).join(Employee).join(Client).filter(
            and_(Client.active == 1, Contract.active == 1, Employee.active == 1)).all()


def reminders_set(payroll_run_date):

    contracts_w = contracts_per_period(period='week')

    contracts_b = contracts_per_period(period='biweek')

    contracts_s = contracts_per_period(period='semimonth')

    contracts_m = contracts_per_period(period='month')
    #
    reminders_set = set()
    for c, cl, em in contracts_w:
        for ws, we in weeks_between_dates(date_to_datetime(c.startdate), payroll_run_date):
            reminders_set.add(reminder_hash(c, ws, we))
    for c, cl, em in contracts_b:
        for ws, we in biweeks_between_dates(date_to_datetime(c.startdate), payroll_run_date):
            reminders_set.add(reminder_hash(c, ws, we))
    for c, cl, em in contracts_s:
        for ws, we in semimonths_between_dates(date_to_datetime(c.startdate), payroll_run_date):
            reminders_set.add(reminder_hash(c, ws, we))
    for c, cl, em in contracts_m:
        for ws, we in months_between_dates(date_to_datetime(c.startdate), payroll_run_date):
            reminders_set.add(reminder_hash(c, ws, we))
    return reminders_set


def reminders(reminder_period_start, payroll_run_date, t_set, period='week'):
    #
    reminders = []
    for c, cl, em in contracts_per_period(period=period):
        if period == 'week':
            for ws, we in weeks_between_dates(reminder_period_start, payroll_run_date):
                if reminder_hash(c, ws, we) not in t_set:
                    reminders.append((c, ws, we))
        elif period == 'biweek':
            for ws, we in biweeks_between_dates(date_to_datetime(c.startdate), payroll_run_date):
                if reminder_hash(c, ws, we) not in t_set:
                    reminders.append((c, ws, we))
        elif period == 'semimonth':
            for ws, we in semimonths_between_dates(date_to_datetime(c.startdate), payroll_run_date):
                if reminder_hash(c, ws, we) not in t_set:
                    reminders.append((c, ws, we))
        else:
            for ws, we in months_between_dates(date_to_datetime(c.startdate), payroll_run_date):
                if reminder_hash(c, ws, we) not in t_set:
                    reminders.append((c, ws, we))

    return reminders


def timecards_set():

    timecards_set = set()
    for t in timecards():

        timecards_set.add(timecard_hash(t[0]))
    return timecards_set