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
"""

def open_invoices(session):
    """
    return list of OPEN invoices
    """
    return session.query(Invoice).filter(Invoice.voided==False, Invoice.posted==True, Invoice.cleared==False, Invoice.mock == False, Invoice.amount > 0)


def picked_open_invoice(session, args):
    o_invoices = open_invoices(session)
    return o_invoices[args.number-1]

