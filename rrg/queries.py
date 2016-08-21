from sqlalchemy import and_

from rrg.models import Contract
from rrg.models import Client
from rrg.models import Employee
from rrg.models import periods
from rrg.models import NotePayment
from rrg.models import Note

periods = {
    'week': 1,
    'semimonth': 2,
    'month': 3,
    'biweek': 5,
}


def contracts_per_period(session, args):
    """
    returns active contracts of period type - weekly, semimonthly, monthly
    and biweekly
    """
    if args.period not in periods:
        print('wrong period type')
    with session.no_autoflush:
        contracts = session.query(Contract, Client, Employee).join(Client) \
            .join(Employee).filter(
            and_(Contract.active == 1, Client.active == 1,
                 Employee.active == 1,
                 Contract.period_id == periods[args.period])).all()
        return contracts


def sheree_notes_payments(session):
    return session.query(NotePayment).filter(
        and_(
            NotePayment.voided == False, NotePayment.employee_id == 1025)) \
        .order_by(NotePayment.date)


def sherees_notes(session):
    return session.query(Note).filter(
        and_(Note.employee_id == 1025, Note.voided == False)).order_by(Note.date)


def sherees_notes_notespayments(session):
    q1 = session.query(NotePayment).filter(
        and_(
            NotePayment.voided == False, NotePayment.employee_id == 1025))
    q2 = session.query(Note).filter(
        and_(Note.employee_id == 1025, Note.voided == False))

    return q1.union(q2).order_by('date')
