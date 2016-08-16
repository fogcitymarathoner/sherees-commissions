from sqlalchemy import and_

from rrg.models import Contract
from rrg.models import Client
from rrg.models import Employee
from rrg.models import periods

from rrg.models import session_maker

periods = {
    'week': 1,
    'semimonth': 2,
    'month': 3,
    'biweek': 5,
}

 
def contracts_per_period(args):
    """
    returns active contracts of period type - weekly, semimonthly, monthly
    and biweekly
    """
    if args.period not in periods:
        print('wrong period type')
    session = session_maker(args)
    with session.no_autoflush:
        return session.query(Contract, Client, Employee).join(Client) \
            .join(Employee).filter(and_(Contract.active == 1, Client.active == 1,
                                        Employee.active == 1, Contract.period_id == periods[period]))
