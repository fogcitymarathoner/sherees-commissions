from rrg.sales import salespersons_notes
from rrg.sales import salespersons_notes_payments

periods = {
    'week': 1,
    'semimonth': 2,
    'month': 3,
    'biweek': 5,
}


def sheree_notes_payments(session, sheree):
    return salespersons_notes_payments(session, sheree)


def sherees_notes(session, sheree):
    return salespersons_notes(session, sheree)
