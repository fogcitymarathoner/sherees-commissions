from sqlalchemy import and_
from datetime import datetime as dt
from datetime import timedelta as td

from rrg.models import Invoice
from rrg.models import Iitem


def delete_old_void_invoices(session, args):
    for i in session.query(
            Invoice).filter(and_(Invoice.voided == True, Invoice.date < dt.now() - td(days=args.days_past))):
        session.delete(i)


def delete_old_zeroed_invoice_items(session, args):
    for ii, i in session.query(
            Iitem, Invoice).filter(and_(Iitem.amount == 0, Invoice.date < dt.now() - td(days=args.days_past))):
        session.delete(ii)
