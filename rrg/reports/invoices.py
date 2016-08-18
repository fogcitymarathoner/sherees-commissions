from datetime import datetime as dt
from sqlalchemy import and_
from rrg.models import Invoice
from rrg.models import Contract
from rrg.models import Client
from rrg.models import Employee


def invoices_year_month(session, args):
    m = int(args.month)
    y = int(args.year)
    if m < 12:
        nexty = y
        nextm = m + 1
    else:
        nexty = int(y) + 1
        nextm = 1

    return session.query(Invoice).filter(
        and_(Invoice.date >= dt(year=y, month=m, day=1),
             Invoice.date < dt(year=nexty, month=nextm, day=1),
             Invoice.voided == False)).all()


def active_contracts(session):
    return session.query(Contract, Client, Employee) \
        .join(Client).join(Employee) \
        .filter(and_(Contract.active == True, Client.active == True,
                     Employee.active == True))
