import sys
from datetime import datetime as dt
import logging
from sqlalchemy import MetaData

from rrg import MYSQL_PORT_3306_TCP_ADDR
from rrg.models import Contract
from rrg.models import Client
from rrg.models import Employee
from rrg.models import periods
from rrg.queries import contracts_per_period
from rrg import session

logging.basicConfig(filename='testing.log', level=logging.DEBUG)
logger = logging.getLogger('test')

metadata = MetaData()


class Test:

    def setup_class(self):

        self.payroll_run_date = dt(year=2016, month=8, day=8)
        logger.debug('Setup test reminders test')
        session.begin_nested()
        client = Client(name='weekly', active=True)
        session.add(client)
        employee = Employee(
            firstname='firstname', lastname='lastname', active=True)
        session.add(employee)

        contract = Contract(employee=employee, client=client, active=True,
                            period_id=periods['week'], startdate=dt.now())
        session.add(contract)
        contract = Contract(employee=employee, client=client, active=True,
                            period_id=periods['biweek'], startdate=dt.now())
        session.add(contract)
        contract = Contract(employee=employee, client=client, active=True,
                            period_id=periods['semimonth'], startdate=dt.now())
        session.add(contract)

        contract = Contract(employee=employee, client=client, active=True,
                            period_id=periods['month'], startdate=dt.now())
        session.add(contract)

    def teardown_class(self):
        logger.debug('Teardown reminders')
        session.rollback()

    def test_in_test(self):
        """
        test _called_from_test
        :return:
        """
        assert sys._called_from_test
        assert 'localhost' == MYSQL_PORT_3306_TCP_ADDR

    def test_models(self, capsys):
        """
        test model interactions
        """
        logger.debug('testing models')

        contracts = contracts_per_period(period='week',
                                         reminder_start_date=dt.strptime(
                                             '1970-01-01', '%Y-%m-%d'))

        logger.debug('employees')
        logger.debug(session.query(Employee).all())
        logger.debug('contracts')
        logger.debug(contracts)
        logger.debug(contracts[0])
        c = contracts[0]
        logger.debug(c[0].startdate)
        assert 1 == len(contracts)


        contracts = contracts_per_period(period='biweek',
                                         reminder_start_date=dt.strptime(
                                             '1970-01-01', '%Y-%m-%d'))
        assert 1 == len(contracts)


        contracts = contracts_per_period(period='semimonth',
                                         reminder_start_date=dt.strptime(
                                             '1970-01-01', '%Y-%m-%d'))
        assert 1 == len(contracts)

        contracts = contracts_per_period(period='month',
                                         reminder_start_date=dt.strptime(
                                             '1970-01-01', '%Y-%m-%d'))
        assert 1 == len(contracts)
