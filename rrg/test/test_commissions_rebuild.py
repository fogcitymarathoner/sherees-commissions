import logging
import sys
from datetime import datetime as dt
from datetime import timedelta as td

from rrg.lib.reminders import biweeks_between_dates
from rrg.lib.reminders import current_semimonth
from rrg.lib.reminders import months_between_dates
from rrg.lib.reminders import semimonths_between_dates
from rrg.lib.reminders import weeks_between_dates
from rrg.lib.reminders_generation import rebuild_empty_invoice_commissions
from rrg.models import Citem
from rrg.models import Client
from rrg.models import Contract
from rrg.models import ContractItem
from rrg.models import Employee
from rrg.models import Iitem
from rrg.models import Invoice
from rrg.models import periods
from rrg.models_api import session_maker

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

            employee_active = Employee(id=1025, firstname='firstname', lastname='lastname', active=True)
            employee_inactive = Employee(id=1479, firstname='firstname', lastname='lastname', active=False)

            objects.append(employee_active)
            objects.append(employee_inactive)

            self.session.bulk_save_objects(objects)

            employees = self.session.query(Employee).all()

            logger.debug('employees[0]')
            logger.debug(employees[0])
            logger.debug('clients[0]')
            logger.debug(clients[0])

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

            objects = []
            contracts = self.session.query(Contract).all()
            logger.debug('contracts')
            logger.debug(contracts[0].id)
            for contract in contracts:
                logger.debug(contract)

            objects.append(
                ContractItem(contract_id=contracts[1].id, amt=10, cost=5,
                         description='weekly %s' % contracts[1].title))

            objects.append(
                ContractItem(contract_id=contracts[2].id, amt=10, cost=5,
                         description='weekly %s' % contracts[2].title))

            objects.append(
                ContractItem(contract_id=contracts[3].id, amt=10, cost=5,
                         description='weekly %s' % contracts[3].title))

            objects.append(
                ContractItem(contract_id=contracts[4].id, amt=10, cost=5,
                         description='weekly %s' % contracts[4].title))

            objects.append(
                ContractItem(contract_id=contracts[5].id, amt=10, cost=5,
                         description='weekly %s' % contracts[5].title))

            objects.append(
                ContractItem(contract_id=contracts[6].id, amt=10, cost=5,
                         description='weekly %s' % contracts[6].title))

            objects.append(
                ContractItem(contract_id=contracts[7].id, amt=10, cost=5,
                         description='weekly %s' % contracts[7].title))

            objects.append(
                ContractItem(contract_id=contracts[8].id, amt=10, cost=5,
                         description='weekly %s' % contracts[8].title))

            objects.append(
                ContractItem(contract_id=contracts[9].id, amt=10, cost=5,
                         description='weekly %s' % contracts[9].title))

            objects.append(
                ContractItem(contract_id=contracts[10].id, amt=10, cost=5,
                         description='weekly %s' % contracts[10].title))

            objects.append(
                ContractItem(contract_id=contracts[11].id, amt=10, cost=5,
                         description='weekly %s' % contracts[11].title))

            self.session.bulk_save_objects(objects)

            objects = []
            weeks = weeks_between_dates(dt(year=2016, month=7, day=4), self.payroll_run_date)
            second_week_start, second_week_end = weeks[1]

            objects.append(
                Invoice(contract_id=contracts[0].id, terms=contracts[0].terms, period_start=second_week_start.date(),
                        period_end=second_week_end.date(),
                        date=self.payroll_run_date.date()))

            objects.append(
                Invoice(contract_id=contracts[4].id, terms=contracts[4].terms, period_start=second_week_start.date(),
                        period_end=second_week_end.date(),
                        date=self.payroll_run_date.date()))
            objects.append(
                Invoice(contract_id=contracts[8].id, terms=contracts[8].terms, period_start=second_week_start.date(),
                        period_end=second_week_end.date(),
                        date=self.payroll_run_date.date()))

            biweeks = biweeks_between_dates(dt(year=2016, month=7, day=4), self.payroll_run_date)

            start, end = biweeks[1]
            objects.append(Invoice(contract_id=contracts[1].id, terms=contracts[1].terms, period_start=start.date(),
                                   period_end=end.date(),
                                   date=self.payroll_run_date.date()))
            objects.append(Invoice(contract_id=contracts[5].id, terms=contracts[5].terms, period_start=start.date(),
                                   period_end=end.date(),
                                   date=self.payroll_run_date.date()))
            objects.append(Invoice(contract_id=contracts[9].id, terms=contracts[9].terms, period_start=start.date(),
                                   period_end=end.date(),
                                   date=self.payroll_run_date.date()))

            semimonths = semimonths_between_dates(dt(year=2016, month=7, day=4), self.payroll_run_date)

            start, end = semimonths[1]
            objects.append(Invoice(contract_id=contracts[2].id, terms=contracts[2].terms, period_start=start.date(),
                                   period_end=end.date(),
                                   date=self.payroll_run_date.date()))
            objects.append(Invoice(contract_id=contracts[6].id, terms=contracts[6].terms, period_start=start.date(),
                                   period_end=end.date(),
                                   date=self.payroll_run_date.date()))
            objects.append(Invoice(contract_id=contracts[10].id, terms=contracts[10].terms, period_start=start.date(),
                                   period_end=end.date(),
                                   date=self.payroll_run_date.date()))

            months = months_between_dates(dt(year=2016, month=7, day=4), self.payroll_run_date)

            start, end = months[1]
            objects.append(Invoice(contract_id=contracts[3].id, terms=contracts[3].terms, period_start=start.date(),
                                   period_end=end.date(),
                                   date=self.payroll_run_date.date()))
            objects.append(Invoice(contract_id=contracts[7].id, terms=contracts[7].terms, period_start=start.date(),
                                   period_end=end.date(),
                                   date=self.payroll_run_date.date()))
            objects.append(Invoice(contract_id=contracts[11].id, terms=contracts[11].terms, period_start=start.date(),
                                   period_end=end.date(),
                                   date=self.payroll_run_date.date()))
            for o in objects:
                logger.debug(o)
            self.session.bulk_save_objects(objects)

            invoices = self.session.query(Invoice).all()

            objects = []

            objects.append(Iitem(invoice_id=invoices[1].id, description='regular',
                                 amount=10, quantity=1, cost=5))
            objects.append(Iitem(invoice_id=invoices[2].id, description='regular',
                                 amount=10, quantity=1, cost=5))
            objects.append(Iitem(invoice_id=invoices[3].id, description='regular',
                                 amount=10, quantity=1, cost=5))
            objects.append(Iitem(invoice_id=invoices[4].id, description='regular',
                                 amount=10, quantity=1, cost=5))
            objects.append(Iitem(invoice_id=invoices[5].id, description='regular',
                                 amount=10, quantity=1, cost=5))
            objects.append(Iitem(invoice_id=invoices[6].id, description='regular',
                                 amount=10, quantity=1, cost=5))
            objects.append(Iitem(invoice_id=invoices[7].id, description='regular',
                                 amount=10, quantity=1, cost=5))
            objects.append(Iitem(invoice_id=invoices[8].id, description='regular',
                                 amount=10, quantity=1, cost=5))
            objects.append(Iitem(invoice_id=invoices[9].id, description='regular',
                                 amount=10, quantity=1, cost=5))
            objects.append(Iitem(invoice_id=invoices[10].id, description='regular',
                                 amount=10, quantity=1, cost=5))
            objects.append(Iitem(invoice_id=invoices[11].id, description='regular',
                                 amount=10, quantity=1, cost=5))


            self.session.bulk_save_objects(objects)
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

    def test_rebuild(self, capsys):
        """
        test building comm items for invoice with or without them
        """
        logger.debug('invoices comm rebuild')
        logger.debug(self.session.query(Invoice).count())
        for i in self.session.query(Invoice).all():
            logger.debug(i)
            rebuild_empty_invoice_commissions(self.session, i)
        logger.debug('comm items')
        logger.debug(self.session.query(Citem).all())
        for i in self.session.query(Citem).all():
            logger.debug(i)
        assert 22 == self.session.query(Citem).count()
