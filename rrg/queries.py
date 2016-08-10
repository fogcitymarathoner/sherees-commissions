from datetime import datetime as dt
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_
from rrg.models import engine
from rrg.models import Contract
from rrg.models import Client
from rrg.models import Employee

Session = sessionmaker(bind=engine)

session = Session()

periods = {
    'week': 1,
    'semimonth': 2,
    'month': 3,
    'biweek': 5,
}

 
def contracts_per_period(period='week'):
    """
    returns active contracts of period type - weekly, semimonthly, monthly and biweekly
    """
    if period not in periods:
        print('wrong period type')
    
    # return session.query(Contract).filter(and_(Contract.period_id == 1, Client.active == 1, Employee.voided == 0, Employee.active is True, Contract.startdate > dt.strptime('1970-01-01', '%Y-%m-%d')))
    return session.query(Contract, Employee, Client).join(Client).join(Employee).filter(Employee.active == 1) \
                .filter(Client.active ==1) \
                .filter(Contract.active ==1) \
                .filter(Contract.period_id == periods[period]) \
                .filter(Contract.startdate > dt.strptime('1970-01-01', '%Y-%m-%d')) \
                .all()
 
