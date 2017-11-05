import logging
from datetime import datetime as dt

from lib import contracts_per_period, biweeks_between_dates, weeks_between_dates, months_between_dates, \
    semimonths_between_dates, reminder_hash, create_invoice_for_period
from rrg.lib.archive import date_to_datetime
from rrg.lib.reminders import biweeks_between_dates
from rrg.lib.reminders import months_between_dates
from rrg.lib.reminders import semimonths_between_dates
from rrg.lib.reminders import weeks_between_dates
from rrg.models import Citem

logging.basicConfig(filename='testing.log', level=logging.DEBUG)
logger = logging.getLogger('test')

logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

"""
this module differs from reminders in that it depends on models
"""


def reminders_set(session, period, payroll_run_date):
    args.period = 'week'
    contracts_w = contracts_per_period(session, period)

    args.period = 'biweek'
    contracts_b = contracts_per_period(session, period)

    args.period = 'semimonth'
    contracts_s = contracts_per_period(session, period)

    args.period = 'month'
    contracts_m = contracts_per_period(session, period)
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




def reminder_to_timecard(session, reminder_period_start, payroll_run_date, t_set, period, number):
    """
    A new invoice is a timecard if voided False and timecard true
    """
    # create voided invoice for number'th reminder from reminders

    reminders_tbs = reminders(session, reminder_period_start, payroll_run_date, t_set, period)

    contract, start, end = reminders_tbs[number - 1]
    new_inv = create_invoice_for_period(session, contract, start, end)
    new_inv.voided = False
    new_inv.mock = False
    new_inv.timecard = True


def forget_reminder(session, reminder_period_start, payroll_run_date, t_set, period, number):
    # create voided invoice for number'th reminder from reminders

    reminders_tbs = reminders(session, reminder_period_start, payroll_run_date, t_set, period)

    contract, start, end = reminders_tbs[number - 1]
    new_inv = create_invoice_for_period(session, contract, start, end)
    new_inv.voided = True


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


