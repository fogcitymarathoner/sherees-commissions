import logging
import sys
from datetime import datetime as dt
from datetime import timedelta as td

from freezegun import freeze_time

from rrg.lib.reminders import biweeks_between_dates
from rrg.lib.reminders import current_semimonth
from rrg.lib.reminders import months_between_dates
from rrg.lib.reminders import semimonths_between_dates
from rrg.lib.reminders import weeks_between_dates
from rrg.lib.reminders_generation import create_invoice_for_period
from rrg.models import Citem
from rrg.models import Client
from rrg.models import ClientMemo
from rrg.models import Contract
from rrg.models import ContractItem
from rrg.models import ContractItemCommItem
from rrg.models import Employee
from rrg.models import EmployeeMemo
from rrg.models import EmployeePayment
from rrg.models import Iitem
from rrg.models import Invoice
from rrg.models import Payroll
from rrg.models import periods
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
            cmemo0 = ClientMemo(client_id=clients[0].id, notes='cl1 memo', date=dt.now())
            cmemo1 = ClientMemo(client_id=clients[1].id, notes='cl2 memo', date=dt.now())
            objects = [cmemo0, cmemo1]

            self.session.bulk_save_objects(objects)
            objects = []

            employee_active = Employee(firstname='firstname', lastname='activelastname', active=True)
            employee_inactive = Employee(firstname='firstname', lastname='inactivelastname', active=False)
            employee_sales_person1 = Employee(firstname='sales', lastname='person1', active=True)
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

            ememo0 = EmployeeMemo(employee_id=employees[0].id, notes='emp1 memo', date=dt.now())
            ememo1 = EmployeeMemo(employee_id=employees[1].id, notes='emp2 memo', date=dt.now())
            ememo2 = EmployeeMemo(employee_id=employees[2].id, notes='emp3 memo', date=dt.now())
            ememo3 = EmployeeMemo(employee_id=employees[3].id, notes='emp4 memo', date=dt.now())
            objects = [ememo0, ememo1, ememo2, ememo3]

            self.session.bulk_save_objects(objects)

            objects = []

            # Active Contract
            objects.append(Contract(employee_id=employees[0].id,
                                    title='weekly-active-client-active-employee',
                                    client_id=clients[0].id,
                                    terms=clients[0].terms, active=True,
                                    period_id=periods['week'],
                                    startdate=self.common_contract_start))

            objects.append(Contract(employee_id=employees[0].id,
                                    title='biweekly-active-client-active-employee',
                                    client_id=clients[0].id,
                                    terms=clients[0].terms, active=True,
                                    period_id=periods['biweek'],
                                    startdate=self.common_contract_start))

            objects.append(Contract(employee_id=employees[0].id,
                                    title='semimonthly-active-client-active-employee',
                                    client_id=clients[0].id,
                                    terms=clients[0].terms, active=True,
                                    period_id=periods['semimonth'],
                                    startdate=self.common_contract_start))

            objects.append(Contract(employee_id=employees[0].id,
                                    title='monthly-active-client-active-employee',
                                    client_id=clients[0].id,
                                    terms=clients[0].terms, active=True,
                                    period_id=periods['month'],
                                    startdate=self.common_contract_start))

            # Active Contracts Inactive Employees
            objects.append(Contract(employee_id=employees[1].id,
                                    title='weekly-inactive-client-inactive-employee',
                                    client_id=clients[1].id,
                                    terms=clients[1].terms, active=True,
                                    period_id=periods['week'],
                                    startdate=self.common_contract_start))

            objects.append(Contract(employee_id=employees[1].id,
                                    title='biweekly-inactive-client-inactive-employee',
                                    client_id=clients[1].id,
                                    terms=clients[1].terms, active=True,
                                    period_id=periods['biweek'],
                                    startdate=self.common_contract_start))

            objects.append(Contract(employee_id=employees[1].id,
                                    title='semimonthly-inactive-client-inactive-employee',
                                    client_id=clients[1].id,
                                    terms=clients[1].terms, active=True,
                                    period_id=periods['semimonth'],
                                    startdate=self.common_contract_start))

            objects.append(Contract(employee_id=employees[1].id,
                                    title='monthly-inactive-client-inactive-employee',
                                    client_id=clients[1].id,
                                    terms=clients[1].terms, active=True,
                                    period_id=periods['month'],
                                    startdate=self.common_contract_start))

            objects.append(
                Contract(employee_id=employees[1].id, client_id=clients[1].id,
                         terms=clients[1].terms, active=False,
                         period_id=periods['week'], title='weekly-inactive',
                         startdate=self.common_contract_start))

            objects.append(
                Contract(employee_id=employees[1].id,
                         title='biweekly-inactive', client_id=clients[1].id,
                         terms=clients[1].terms, active=False,
                         period_id=periods['biweek'],
                         startdate=self.common_contract_start))

            objects.append(Contract(employee_id=employees[1].id,
                                    title='semimonthly-inactive',
                                    client_id=clients[1].id,
                                    terms=clients[1].terms,
                                    active=False,
                                    period_id=periods['semimonth'],
                                    startdate=self.common_contract_start))

            objects.append(
                Contract(employee_id=employees[1].id, title='monthly-inactive',
                         client_id=clients[1].id,
                         terms=clients[1].terms, active=False,
                         period_id=periods['month'],
                         startdate=self.common_contract_start))

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
                    ContractItem(contract_id=contracts[i].id,
                                 description='Regular', amt=10, active=True,
                                 cost=5))
                objects.append(
                    ContractItem(contract_id=contracts[i].id,
                                 description='Double Time', amt=20,
                                 active=True, cost=10))

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
                    ContractItemCommItem(employee_id=employees[2].id,
                                         contract_item_id=contract_items[i].id,
                                         percent=38.5))

                objects.append(
                    ContractItemCommItem(employee_id=employees[3].id,
                                         contract_item_id=contract_items[i].id,
                                         percent=61.5))

            self.session.bulk_save_objects(objects)

            # invoices
            weeks = weeks_between_dates(dt(year=2016, month=7, day=4),
                                        self.payroll_run_date)
            second_week_start, second_week_end = weeks[1]

            create_invoice_for_period(self.session, contracts[0],
                                      second_week_start.date(),
                                      second_week_end.date(),
                                      date=self.payroll_run_date.date())
            create_invoice_for_period(self.session, contracts[4],
                                      second_week_start.date(),
                                      second_week_end.date(),
                                      date=self.payroll_run_date.date())
            create_invoice_for_period(self.session, contracts[8],
                                      second_week_start.date(),
                                      second_week_end.date(),
                                      date=self.payroll_run_date.date())

            biweeks = biweeks_between_dates(dt(year=2016, month=7, day=4),
                                            self.payroll_run_date)

            start, end = biweeks[1]
            create_invoice_for_period(self.session, contracts[1], start.date(),
                                      end.date(),
                                      date=self.payroll_run_date.date())
            create_invoice_for_period(self.session, contracts[5], start.date(),
                                      end.date(),
                                      date=self.payroll_run_date.date())
            create_invoice_for_period(self.session, contracts[9], start.date(),
                                      end.date(),
                                      date=self.payroll_run_date.date())

            semimonths = semimonths_between_dates(
                dt(year=2016, month=7, day=4), self.payroll_run_date)

            start, end = semimonths[1]
            create_invoice_for_period(self.session, contracts[2], start.date(),
                                      end.date(),
                                      date=self.payroll_run_date.date())
            create_invoice_for_period(self.session, contracts[6], start.date(),
                                      end.date(),
                                      date=self.payroll_run_date.date())
            create_invoice_for_period(self.session, contracts[10],
                                      start.date(), end.date(),
                                      date=self.payroll_run_date.date())

            months = months_between_dates(dt(year=2016, month=7, day=4),
                                          self.payroll_run_date)

            start, end = months[1]
            create_invoice_for_period(self.session, contracts[3], start.date(),
                                      end.date(),
                                      date=self.payroll_run_date.date())
            create_invoice_for_period(self.session, contracts[7], start.date(),
                                      end.date(),
                                      date=self.payroll_run_date.date())
            create_invoice_for_period(self.session, contracts[11],
                                      start.date(), end.date(),
                                      date=self.payroll_run_date.date())

            invoices = self.session.query(Invoice).all()
            logger.debug('INVOICES CREATED')
            pr = Payroll(name='test pr', notes='bogus notes', amount=22.0, date=dt.now())
            self.session.bulk_save_objects([pr])
            payrolls = self.session.query(Payroll).all()
            for i in invoices:
                logger.debug(i)
            epay0 = EmployeePayment(employee_id=employees[0].id, amount=1.0, date=dt.now(), invoice_id=invoices[0].id,
                                    payroll_id=payrolls[0].id)
            epay1 = EmployeePayment(employee_id=employees[1].id, amount=2.0, date=dt.now(), invoice_id=invoices[1].id,
                                    payroll_id=payrolls[0].id)
            objects = [epay0, epay1]

            self.session.bulk_save_objects(objects)

            months_between_dates(self.payroll_run_date, self.payroll_run_date)

            current_semimonth(dt(year=self.payroll_run_date.year,
                                 month=self.payroll_run_date.month, day=16))

            assert not weeks_between_dates(self.payroll_run_date + td(days=1),
                                           self.payroll_run_date)

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

    def test_client_delete_cascade(self):
        """
        test delete cascade of client
        :return:
        """

        assert 12 == self.session.query(Invoice).count()
        assert 24 == self.session.query(Iitem).count()
        assert 48 == self.session.query(Citem).count()
        assert 12 == self.session.query(Contract).count()
        assert 4 == self.session.query(Employee).count()
        assert 2 == self.session.query(Client).count()
        assert 2 == self.session.query(ClientMemo).count()
        assert 2 == self.session.query(EmployeePayment).count()
        assert 4 == self.session.query(EmployeeMemo).count()
        assert 48 == self.session.query(ContractItemCommItem).count()
        assert 1 == self.session.query(Payroll).count()
        logger.debug('DELETECLIENT')
        delcl = self.session.query(Client)[0]
        logger.debug(delcl)

        with self.session.no_autoflush:
            self.session.delete(self.session.query(Client)[0])
        assert 4 == self.session.query(Employee).count()
        assert 8 == self.session.query(Contract).count()
        assert 8 == self.session.query(Invoice).count()
        assert 16 == self.session.query(Iitem).count()
        assert 32 == self.session.query(Citem).count()
        assert 1 == self.session.query(Client).count()
        assert 1 == self.session.query(ClientMemo).count()
        assert 1 == self.session.query(EmployeePayment).count()
        assert 4 == self.session.query(EmployeeMemo).count()
        assert 32 == self.session.query(ContractItemCommItem).count()
        assert 1 == self.session.query(Payroll).count()
