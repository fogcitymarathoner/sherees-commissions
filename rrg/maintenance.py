from sqlalchemy import and_
from datetime import datetime as dt
from datetime import timedelta as td

from rrg.models import Invoice
from rrg.models import Iitem


def delete_old_void_invoices(session, past_days):
    for i in session.query(
            Invoice).filter(and_(Invoice.voided == True, Invoice.date < dt.now() - td(days=past_days))):
        session.delete(i)


def delete_old_zeroed_invoice_items(session, past_days):
    for ii, i in session.query(
            Iitem, Invoice).filter(and_(Iitem.amount == 0, Invoice.date < dt.now() - td(days=past_days))):
        session.delete(ii)
