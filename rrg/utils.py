from rrg import session
from rrg.models import Contract

from rrg.models import Base
from rrg import engine

from rrg.reminders_generation import timecards_set
from rrg.reminders_generation import reminders

from tabulate import tabulate
from datetime import datetime as dt

def clear_out_bad_contracts():
    """
    removed contracts from the database that have either employee_id or client_id 0 or None
    """
    session.query(Contract).filter(Contract.employee_id == 0, Contract.client_id ==0).delete(synchronize_session=False)
    session.commit()


def create_db():
    """
    this routine has a bug, DATABASE isn't fully integrated right, the line

        DATABASE = 'rrg' in rrg/__init__.py has to be temporarily hardcoded to 'rrg_test' or whatever
    :return:
    """
    Base.metadata.create_all(engine)


def week_reminders():
    t_set = timecards_set()
    wreminders = reminders(dt.now() - td(days=90), dt.now(), t_set, 'week')
    tbl = []
    for r in wreminders:
        tbl.append([r[0].client.name, r[0].employee.firstname+' '+r[0].employee.lastname,
            dt.strftime(r[1], '%m/%d/%Y'), dt.strftime(r[2], '%m/%d/%Y')])
    print(tabulate(tbl, headers=['client', 'employee', 'start', 'end']))
