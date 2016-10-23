from sqlalchemy import and_
from rrg.models import NotePayment
from rrg.models import Note


def salespersons_notes_payments(session, salesperson):
    return session.query(NotePayment).filter(
        and_(
            NotePayment.voided == False, NotePayment.employee_id == salesperson.id)) \
        .order_by(NotePayment.date)


def salespersons_notes_payments(session, salesperson):
    return session.query(Note).filter(
        and_(Note.employee_id == salesperson.id, Note.voided == False)).order_by(Note.date)

