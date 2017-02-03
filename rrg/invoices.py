
import logging

from rrg.models import Invoice

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

