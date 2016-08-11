import sys
from datetime import datetime as dt

import logging

from rrg import MYSQL_PORT_3306_TCP_ADDR
from rrg.models import Contract
from rrg.models import Client
from rrg.models import Employee
from rrg.models import periods
from rrg import session

logging.basicConfig(filename='testing.log', level=logging.DEBUG)
logger = logging.getLogger('test')


class Test:


    def setup_class(self):

        self.payroll_run_date = dt(year=2016, month=8, day=8)
        logger.debug('Setup test db')

    def teardown_class(self):
        logger.debug('Teardown test db')

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
        logger.debug(self.payroll_run_date.weekday())

        contracts = session.query(Contract, Employee, Client).join(Client).join(Employee).filter(Employee.active == 1) \
            .filter(Client.active == 1) \
            .filter(Contract.active == 1) \
            .filter(Contract.period_id == periods['week']) \
            .filter(Contract.startdate > dt.strptime('1970-01-01', '%Y-%m-%d')) \
            .all()

        logger.debug(contracts)
        assert False