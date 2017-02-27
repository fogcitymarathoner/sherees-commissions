from datetime import datetime as dt
from datetime import timedelta as td

import logging

from tabulate import tabulate

from rrg.models import Invoice

logging.basicConfig(filename='testing.log', level=logging.DEBUG)
logger = logging.getLogger('test')

logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

"""
Basic functions for Invoice Model
"""


def open_invoices(session):
    """
    return list of OPEN invoices
    """
    return session.query(Invoice).filter(
        Invoice.voided==False, Invoice.posted==True, Invoice.cleared==False, Invoice.mock == False, Invoice.amount > 0)


def pastdue_invoices(session):
    """
    return list of PastDue invoices
    """
    res = []
    oinvs = open_invoices(session)
    for oi in oinvs:
        if Invoice.duedate(oi) <= dt.now():
            res.append(oi)
    return res


def picked_open_invoice(session, args):
    o_invoices = open_invoices(session)
    return o_invoices[args.number-1]


def tabulate_invoices(invoices):
    """
    Return given invoices list tabulated
    :param invoices:
    :return:
    """
    tbl = []
    i = 1
    for r in invoices:
        tbl.append(
            [i, r.id, r.contract.client.name, r.contract.employee.firstname + ' ' +
             r.contract.employee.lastname,
             dt.strftime(r.period_start, '%m/%d/%Y'), dt.strftime(r.period_end, '%m/%d/%Y'),
             r.date, r.date + td(days=r.contract.terms), r.amount])
        i += 1
    return tabulate(tbl, headers=['number', 'sqlid', 'client', 'employee', 'start', 'end', 'date', 'duedate', 'amount'])
