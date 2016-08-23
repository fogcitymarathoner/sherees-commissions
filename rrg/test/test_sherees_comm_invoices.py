import sys
from datetime import datetime as dt
from datetime import timedelta as td
import logging
from freezegun import freeze_time

from rrg import MYSQL_PORT_3306_TCP_ADDR
from rrg.models import Contract
from rrg.models import ContractItem
from rrg.models import ContractItemCommItem
from rrg.models import Client
from rrg.models import Employee
from rrg.models import Invoice
from rrg.models import periods
from rrg.reminders import weeks_between_dates
from rrg.reminders import biweeks_between_dates
from rrg.reminders import semimonths_between_dates
from rrg.reminders import months_between_dates
from rrg.reminders import current_semimonth
from rrg.reminders_generation import create_invoice_for_period
from rrg.sherees_commissions import sherees_contracts_of_interest
from rrg.sherees_commissions import sherees_invoices_of_interest
from rrg.models import session_maker

logging.basicConfig(filename='testing.log', level=logging.DEBUG)
logger = logging.getLogger('test')

logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


class Args(object):
    mysql_host = 'localhost'
    mysql_port = 3306
    db_user = 'root'
    db_pass = 'my_very_secret_password'
    db = 'rrg_test'


class Test:
    @freeze_time("2016-08-08")
    def setup_class(self):

        assert sys._called_from_test

        self.payroll_run_date = dt(year=2016, month=8, day=8)
        self.common_contract_start = dt(year=2016, month=7, day=1)
        logger.debug('Setup test reminders test')
        self.args = Args()

        self.session = session_maker(self.args)
        self.session.begin_nested()
        with self.session.no_autoflush:
            objects = []
            client_active = Client(name='weekly', active=True, terms=30)
            client_inactive = Client(name='weekly-inactive', active=False, terms=30)
            objects.append(client_active)
            objects.append(client_inactive)

            self.session.bulk_save_objects(objects)

            clients = self.session.query(Client).all()

            objects = []

            employee_active = Employee(firstname='firstname', lastname='activelastname', active=True)
            employee_inactive = Employee(firstname='firstname', lastname='inactivelastname', active=False)
            employee_sales_person1 = Employee(id=1025, firstname='sheree', lastname='neoh', active=True)
            employee_sales_person2 = Employee(firstname='sales', lastname='person2', active=True)

            objects.append(employee_active)
            objects.append(employee_inactive)
            objects.append(employee_sales_person1)
            objects.append(employee_sales_person2)

            self.session.bulk_save_objects(objects)

            employees = self.session.query(Employee).all()
            logger.debug('employees')
            for employee in employees:
                logger.debug(employee)

            objects = []

            # Active Contract
            objects.append(Contract(employee_id=employees[0].id, title='weekly-active-client-active-employee',
                                    client_id=clients[0].id, terms=clients[0].terms, active=True,
                                    period_id=periods['week'], startdate=self.common_contract_start))

            objects.append(Contract(employee_id=employees[0].id, title='biweekly-active-client-active-employee',
                                    client_id=clients[0].id, terms=clients[0].terms, active=True,
                                    period_id=periods['biweek'], startdate=self.common_contract_start))

            objects.append(Contract(employee_id=employees[0].id, title='semimonthly-active-client-active-employee',
                                    client_id=clients[0].id, terms=clients[0].terms, active=True,
                                    period_id=periods['semimonth'], startdate=self.common_contract_start))

            objects.append(Contract(employee_id=employees[0].id, title='monthly-active-client-active-employee',
                                    client_id=clients[0].id, terms=clients[0].terms, active=True,
                                    period_id=periods['month'], startdate=self.common_contract_start))

            # Active Contracts Inactive Employees
            objects.append(Contract(employee_id=employees[1].id, title='weekly-inactive-client-inactive-employee',
                                    client_id=clients[1].id, terms=clients[1].terms, active=True,
                                    period_id=periods['week'], startdate=self.common_contract_start))

            objects.append(Contract(employee_id=employees[1].id, title='biweekly-inactive-client-inactive-employee',
                                    client_id=clients[1].id, terms=clients[1].terms, active=True,
                                    period_id=periods['biweek'], startdate=self.common_contract_start))

            objects.append(Contract(employee_id=employees[1].id, title='semimonthly-inactive-client-inactive-employee',
                                    client_id=clients[1].id, terms=clients[1].terms, active=True,
                                    period_id=periods['semimonth'], startdate=self.common_contract_start))

            objects.append(Contract(employee_id=employees[1].id, title='monthly-inactive-client-inactive-employee',
                                    client_id=clients[1].id, terms=clients[1].terms, active=True,
                                    period_id=periods['month'], startdate=self.common_contract_start))

            objects.append(
                Contract(employee_id=employees[1].id, client_id=clients[1].id, terms=clients[1].terms, active=False,
                         period_id=periods['week'], title='weekly-inactive',
                         startdate=self.common_contract_start))

            objects.append(
                Contract(employee_id=employees[1].id, title='biweekly-inactive', client_id=clients[1].id,
                         terms=clients[1].terms, active=False,
                         period_id=periods['biweek'], startdate=self.common_contract_start))

            objects.append(Contract(employee_id=employees[1].id, title='semimonthly-inactive', client_id=clients[1].id,
                                    terms=clients[1].terms,
                                    active=False,
                                    period_id=periods['semimonth'], startdate=self.common_contract_start))

            objects.append(
                Contract(employee_id=employees[1].id, title='monthly-inactive', client_id=clients[1].id,
                         terms=clients[1].terms, active=False,
                         period_id=periods['month'], startdate=self.common_contract_start))

            self.session.bulk_save_objects(objects)

            contracts = self.session.query(Contract).all()
            logger.debug('contracts')
            logger.debug(contracts[0].id)
            for contract in contracts:
                logger.debug(contract)

            # contract items
            objects = []
            for i in xrange(0, 12):
                objects.append(
                    ContractItem(contract_id=contracts[i].id, description='Regular', amt=10, active=True, cost=5))
                objects.append(
                    ContractItem(contract_id=contracts[i].id, description='Double Time', amt=20, active=True, cost=10))

            self.session.bulk_save_objects(objects)
            contract_items = self.session.query(ContractItem).all()
            logger.debug('contract items')
            logger.debug(contract_items[0].id)
            for contract_item in contract_items:
                logger.debug(contract_item)

            # contract items commissions items
            objects = []
            for i in xrange(0, 24):
                objects.append(
                    ContractItemCommItem(employee_id=employees[2].id, contract_item_id=contract_items[i].id,
                                         percent=38.5))

                objects.append(
                    ContractItemCommItem(employee_id=employees[3].id, contract_item_id=contract_items[i].id,
                                         percent=61.5))

                self.session.bulk_save_objects(objects)

            # invoices
            weeks = weeks_between_dates(dt(year=2016, month=7, day=4), self.payroll_run_date)
            second_week_start, second_week_end = weeks[1]

            create_invoice_for_period(self.session, contracts[0], second_week_start.date(), second_week_end.date(), date=self.payroll_run_date.date())
            create_invoice_for_period(self.session, contracts[4], second_week_start.date(), second_week_end.date(), date=self.payroll_run_date.date())
            create_invoice_for_period(self.session, contracts[8], second_week_start.date(), second_week_end.date(), date=self.payroll_run_date.date())

            biweeks = biweeks_between_dates(dt(year=2016, month=7, day=4), self.payroll_run_date)

            start, end = biweeks[1]
            create_invoice_for_period(self.session, contracts[1], start.date(), end.date(), date=self.payroll_run_date.date())
            create_invoice_for_period(self.session, contracts[5], start.date(), end.date(), date=self.payroll_run_date.date())
            create_invoice_for_period(self.session, contracts[9], start.date(), end.date(), date=self.payroll_run_date.date())

            semimonths = semimonths_between_dates(dt(year=2016, month=7, day=4), self.payroll_run_date)

            start, end = semimonths[1]
            create_invoice_for_period(self.session, contracts[2], start.date(), end.date(), date=self.payroll_run_date.date())
            create_invoice_for_period(self.session, contracts[6], start.date(), end.date(), date=self.payroll_run_date.date())
            create_invoice_for_period(self.session, contracts[10], start.date(), end.date(), date=self.payroll_run_date.date())


            months = months_between_dates(dt(year=2016, month=7, day=4), self.payroll_run_date)

            start, end = months[1]
            create_invoice_for_period(self.session, contracts[3], start.date(), end.date(), date=self.payroll_run_date.date())
            create_invoice_for_period(self.session, contracts[7], start.date(), end.date(), date=self.payroll_run_date.date())
            create_invoice_for_period(self.session, contracts[11], start.date(), end.date(), date=self.payroll_run_date.date())

            months_between_dates(self.payroll_run_date, self.payroll_run_date)

            current_semimonth(dt(year=self.payroll_run_date.year, month=self.payroll_run_date.month, day=16))

            assert not weeks_between_dates(self.payroll_run_date + td(days=1), self.payroll_run_date)

    def teardown_class(self):
        logger.debug('Teardown reminders')
        self.session.rollback()
        self.session.flush()

    def test_in_test(self):
        """
        test _called_from_test
        :return:
        """
        assert sys._called_from_test
        assert 'localhost' == MYSQL_PORT_3306_TCP_ADDR

    def test_sherees_contracts_of_interest(self):
        """
        test xml output of invoice
        :return:
        """
        invoices = sherees_invoices_of_interest(self.session)
        print(contract_clients)
        cids = []
        for con, cl in contract_clients:
            print(con)
            cids.append(con.id)
        invs = self.session.query(Invoice).join(Contract).filter(Invoice.contract_id.in_(cids))
        for i in invs:
            print(i)

        assert 1 == 2

    def test_sherees_contracts_of_interest(self):
        """
        test xml output of invoice
        :return:
        """
        contracts = sherees_contracts_of_interest(self.session)
        assert 4 == contracts.count()

    def test_sherees_invoices_of_interest(self):
        invs = sherees_invoices_of_interest(self.session)
        assert 4 == invs.count()
