import sys
from datetime import datetime as dt
from datetime import timedelta as td
import logging
from sqlalchemy import MetaData
from tabulate import tabulate

from rrg import MYSQL_PORT_3306_TCP_ADDR
from rrg.models import Contract
from rrg.models import Client
from rrg.models import Employee
from rrg.models import Invoice
from rrg.models import periods
from rrg.helpers import date_to_datetime
from rrg.reminders import weeks_between_dates
from rrg.reminders import biweeks_between_dates
from rrg.reminders import semimonths_between_dates
from rrg.reminders import months_between_dates
from rrg.queries import contracts_per_period
from rrg.reminders_generation import timecard_hash
from rrg.reminders_generation import reminder_hash
from rrg.reminders_generation import reminders_set
from rrg.reminders_generation import reminders
from rrg.reminders_generation import timecards_set
from rrg.reminders_generation import timecards
from rrg import session

logging.basicConfig(filename='testing.log', level=logging.DEBUG)
logger = logging.getLogger('test')

metadata = MetaData()


class Test:
    def setup_class(self):

        self.payroll_run_date = dt(year=2016, month=8, day=8)
        self.common_contract_start = dt(year=2016, month=7, day=1)
        logger.debug('Setup test reminders test')
        session.begin_nested()
        with session.no_autoflush:
            objects = []
            client_active = Client(name='weekly', active=True)
            client_inactive = Client(name='weekly-inactive', active=False)
            objects.append(client_active)
            objects.append(client_inactive)

            session.bulk_save_objects(objects)

            clients = session.query(Client).all()

            objects = []

            employee_active = Employee(firstname='firstname', lastname='lastname', active=True)
            employee_inactive = Employee(firstname='firstname', lastname='lastname', active=False)

            objects.append(employee_active)
            objects.append(employee_inactive)

            session.bulk_save_objects(objects)

            employees = session.query(Employee).all()

            logger.debug('employees[0]')
            logger.debug(employees[0])
            logger.debug('clients[0]')
            logger.debug(clients[0])

            objects = []

            # Active Contracts
            objects.append(Contract(employee_id=employees[0].id, title='weekly-active-client-active-employee',
                                    client_id=clients[0].id, active=True,
                                    period_id=periods['week'], startdate=self.common_contract_start))

            objects.append(Contract(employee_id=employees[0].id, title='biweekly-active-client-active-employee',
                                    client_id=clients[0].id, active=True,
                                    period_id=periods['biweek'], startdate=self.common_contract_start))

            objects.append(Contract(employee_id=employees[0].id, title='semimonthly-active-client-active-employee',
                                    client_id=clients[0].id, active=True,
                                    period_id=periods['semimonth'], startdate=self.common_contract_start))

            objects.append(Contract(employee_id=employees[0].id, title='monthly-active-client-active-employee',
                                    client_id=clients[0].id, active=True,
                                    period_id=periods['month'], startdate=self.common_contract_start))

            # Active Contracts Inactive Employees
            objects.append(Contract(employee_id=employees[1].id, title='weekly-inactive-client-inactive-employee',
                                    client_id=clients[1].id, active=True,
                                    period_id=periods['week'], startdate=self.common_contract_start))

            objects.append(Contract(employee_id=employees[1].id, title='biweekly-inactive-client-inactive-employee',
                                    client_id=clients[1].id, active=True,
                                    period_id=periods['biweek'], startdate=self.common_contract_start))

            objects.append(Contract(employee_id=employees[1].id, title='semimonthly-inactive-client-inactive-employee',
                                    client_id=clients[1].id, active=True,
                                    period_id=periods['semimonth'], startdate=self.common_contract_start))

            objects.append(Contract(employee_id=employees[1].id, title='monthly-inactive-client-inactive-employee',
                                    client_id=clients[1].id, active=True,
                                    period_id=periods['month'], startdate=self.common_contract_start))

            objects.append(Contract(employee_id=employees[1].id, client_id=clients[1].id, active=False,
                                    period_id=periods['week'], title='weekly-inactive',
                                    startdate=self.common_contract_start))

            objects.append(
                Contract(employee_id=employees[1].id, title='biweekly-inactive', client_id=clients[1].id, active=False,
                         period_id=periods['biweek'], startdate=self.common_contract_start))

            objects.append(Contract(employee_id=employees[1].id, title='semimonthly-inactive', client_id=clients[1].id,
                                    active=False,
                                    period_id=periods['semimonth'], startdate=self.common_contract_start))

            objects.append(
                Contract(employee_id=employees[1].id, title='monthly-inactive', client_id=clients[1].id, active=False,
                         period_id=periods['month'], startdate=self.common_contract_start))

            session.bulk_save_objects(objects)

            objects = []
            contracts = session.query(Contract).all()
            logger.debug('contracts')

            for contract in session.query(Contract).all():
                logger.debug(contract)

            weeks = weeks_between_dates(dt(year=2016, month=7, day=4), self.payroll_run_date)

            second_week_start, second_week_end = weeks[1]
            objects.append(Invoice(contract=contracts[0], period_start=second_week_start, period_end=second_week_end))
            objects.append(Invoice(contract=contracts[4], period_start=second_week_start, period_end=second_week_end))
            objects.append(Invoice(contract=contracts[8], period_start=second_week_start, period_end=second_week_end))

            biweeks = biweeks_between_dates(dt(year=2016, month=7, day=4), self.payroll_run_date)

            start, end = biweeks[1]
            objects.append(Invoice(contract=contracts[1], period_start=start, period_end=end))
            objects.append(Invoice(contract=contracts[5], period_start=start, period_end=end))
            objects.append(Invoice(contract=contracts[9], period_start=start, period_end=end))

            semimonths = semimonths_between_dates(dt(year=2016, month=7, day=4), self.payroll_run_date)

            start, end = semimonths[1]
            objects.append(Invoice(contract=contracts[2], period_start=start, period_end=end))
            objects.append(Invoice(contract=contracts[6], period_start=start, period_end=end))
            objects.append(Invoice(contract=contracts[10], period_start=start, period_end=end))

            months = months_between_dates(dt(year=2016, month=7, day=4), self.payroll_run_date)

            start, end = months[1]
            objects.append(Invoice(contract=contracts[3], period_start=start, period_end=end))
            objects.append(Invoice(contract=contracts[7], period_start=start, period_end=end))
            objects.append(Invoice(contract=contracts[11], period_start=start, period_end=end))

            session.bulk_save_objects(objects)

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

        contracts_w = contracts_per_period(period='week')

        logger.debug('employees')
        logger.debug(session.query(Employee).all())
        logger.debug('contracts')
        #
        for contract, client, employee in contracts_w:
            logger.debug(contract)
            logger.debug(client)
            logger.debug(employee)

        assert 1 == contracts_w.count()

        contracts_b = contracts_per_period(period='biweek')
        assert 1 == contracts_b.count()

        contracts_s = contracts_per_period(period='semimonth')
        assert 1 == contracts_s.count()

        contracts_m = contracts_per_period(period='month')
        assert 1 == contracts_m.count()

        logger.debug('timecards')
        tbl = []
        r_set = reminders_set(self.payroll_run_date)
        tcards = timecards()
        t_set = timecards_set()
        for t in tcards:
            logger.debug(t)
            tbl.append([t[0].id, t[0].period_start, t[0].period_end, t[1].active, t[1].title, t[2].active, t[3].active, 1 if timecard_hash(t[0]) in r_set else 0,
                        timecard_hash(t[0])])
        logger.debug(tabulate(tbl,
                              headers=['id', 'start', 'end', 'contract-active', 'contract-title', 'employee-active',
                                       'client-active', 'already-has-reminder', 'timecard-hash']))
        # weekly
        assert dt(year=2016, month=7, day=11) == date_to_datetime(tcards[0][0].period_start)
        assert dt(year=2016, month=7, day=17) == date_to_datetime(tcards[0][0].period_end)
        assert True is tcards[0][1].active
        assert True is tcards[0][2].active
        assert True is tcards[0][3].active
        # biweekly
        assert dt(year=2016, month=7, day=11) == date_to_datetime(tcards[1][0].period_start)
        assert dt(year=2016, month=7, day=24) == date_to_datetime(tcards[1][0].period_end)
        assert True is tcards[1][1].active
        assert True is tcards[1][2].active
        assert True is tcards[1][3].active
        # semimonthly
        assert dt(year=2016, month=7, day=16) == date_to_datetime(tcards[2][0].period_start)
        assert dt(year=2016, month=7, day=31) == date_to_datetime(tcards[2][0].period_end)
        assert True is tcards[2][1].active
        assert True is tcards[2][2].active
        assert True is tcards[2][3].active
        # monthly
        assert dt(year=2016, month=8, day=1) == date_to_datetime(tcards[3][0].period_start)
        assert dt(year=2016, month=8, day=31) == date_to_datetime(tcards[3][0].period_end)
        assert True is tcards[3][1].active
        assert True is tcards[3][2].active
        assert True is tcards[3][3].active


        logger.debug('biweekly')
        for c, ws, we in reminders(self.payroll_run_date - td(days=30), self.payroll_run_date, t_set, period='biweek'):
            logger.debug('%s %s %s' % (c, ws, we))
        logger.debug('semimonthly')
        for c, ws, we in reminders(self.payroll_run_date - td(days=30), self.payroll_run_date, t_set, period='semimonth'):
            logger.debug('%s %s %s' % (c, ws, we))
        logger.debug('monthly')
        for c, ws, we in reminders(self.payroll_run_date - td(days=30), self.payroll_run_date, t_set, period='month'):
            logger.debug('%s %s %s' % (c, ws, we))

        reminders_to_be_sent = reminders(self.payroll_run_date - td(days=30), self.payroll_run_date, t_set, period='week')

        # weekly

        logger.debug('weekly')
        for c, ws, we in reminders_to_be_sent:
            logger.debug('%s %s %s' % (c, ws, we))

        assert dt(year=2016, month=7, day=4) == reminders_to_be_sent[0][1]
        assert dt(year=2016, month=7, day=10) == reminders_to_be_sent[0][2]
        assert True is reminders_to_be_sent[0][0].active
        assert True is reminders_to_be_sent[0][0].employee.active
        assert True is reminders_to_be_sent[0][0].client.active

        # skipped 7/11 - 7/17
        assert dt(year=2016, month=7, day=18) == reminders_to_be_sent[1][1]
        assert dt(year=2016, month=7, day=24) == reminders_to_be_sent[1][2]
        assert True is reminders_to_be_sent[1][0].active
        assert True is reminders_to_be_sent[1][0].employee.active
        assert True is reminders_to_be_sent[1][0].client.active

        # biweekly

        reminders_to_be_sent = reminders(self.payroll_run_date - td(days=30), self.payroll_run_date, t_set, period='biweek')
        assert dt(year=2016, month=6, day=27) == reminders_to_be_sent[0][1]
        assert dt(year=2016, month=7, day=10) == reminders_to_be_sent[0][2]
        assert True is reminders_to_be_sent[0][0].active
        assert True is reminders_to_be_sent[0][0].employee.active
        assert True is reminders_to_be_sent[0][0].client.active

        # skipped 7/11 - 7/24

        assert dt(year=2016, month=7, day=25) == reminders_to_be_sent[1][1]
        assert dt(year=2016, month=8, day=7) == reminders_to_be_sent[1][2]
        assert True is reminders_to_be_sent[1][0].active
        assert True is reminders_to_be_sent[1][0].employee.active
        assert True is reminders_to_be_sent[1][0].client.active

        # semimonthly
        reminders_to_be_sent = reminders(self.payroll_run_date - td(days=30), self.payroll_run_date, t_set, period='semimonth')
        assert dt(year=2016, month=7, day=1) == reminders_to_be_sent[0][1]
        assert dt(year=2016, month=7, day=15) == reminders_to_be_sent[0][2]
        assert True is reminders_to_be_sent[0][0].active
        assert True is reminders_to_be_sent[0][0].employee.active
        assert True is reminders_to_be_sent[0][0].client.active

        # skipped 7/15 - 7/31
        assert dt(year=2016, month=8, day=1) == reminders_to_be_sent[1][1]
        assert dt(year=2016, month=8, day=15) == reminders_to_be_sent[1][2]
        assert True is reminders_to_be_sent[1][0].active
        assert True is reminders_to_be_sent[1][0].employee.active
        assert True is reminders_to_be_sent[1][0].client.active

        # monthly

        reminders_to_be_sent = reminders(self.payroll_run_date - td(days=30), self.payroll_run_date, t_set, period='month')
        assert dt(year=2016, month=7, day=1) == reminders_to_be_sent[0][1]
        assert dt(year=2016, month=7, day=31) == reminders_to_be_sent[0][2]
        assert True is reminders_to_be_sent[0][0].active
        assert True is reminders_to_be_sent[0][0].employee.active
        assert True is reminders_to_be_sent[0][0].client.active
        # Second month missing
        assert 1 == len(reminders_to_be_sent)

