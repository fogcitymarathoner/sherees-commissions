from datetime import datetime as dt

from rrg.models import Contract
from rrg.models import Client
from rrg.models import Employee
from rrg.models import periods

from rrg import session

periods = {
    'week': 1,
    'semimonth': 2,
    'month': 3,
    'biweek': 5,
}

 
def contracts_per_period(
        period='week', reminder_start_date=dt.strptime(
            '1970-01-01', '%Y-%m-%d')):
    """
    returns active contracts of period type - weekly, semimonthly, monthly
    and biweekly
    """
    if period not in periods:
        print('wrong period type')
    return session.query(Contract, Employee, Client).join(Client) \
        .join(Employee).filter(Employee.active == 1) \
        .filter(Client.active == 1) \
        .filter(Contract.active == 1) \
        .filter(Contract.period_id == periods[period]) \
        .filter(Contract.startdate >= reminder_start_date).all()

