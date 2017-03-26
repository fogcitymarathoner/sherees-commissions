import logging
import sys
import xml.etree.ElementTree as ET
from datetime import datetime as dt
from datetime import timedelta as td

from freezegun import freeze_time

from rrg.utils import doc_attach_collected_contracts
from rrg.lib.reminders import biweeks_between_dates
from rrg.lib.reminders import current_semimonth
from rrg.lib.reminders import months_between_dates
from rrg.lib.reminders import semimonths_between_dates
from rrg.lib.reminders import weeks_between_dates
from rrg.lib.reminders_generation import create_invoice_for_period
from rrg.models import Citem
from rrg.models import Client
from rrg.models import ClientCheck
from rrg.models import ClientMemo
from rrg.models import Contract
from rrg.models import ContractItem
from rrg.models import ContractItemCommItem
from rrg.models import Employee
from rrg.models import EmployeeMemo
from rrg.models import EmployeePayment
from rrg.models import Iitem
from rrg.models import Invoice
from rrg.models import InvoicePayment
from rrg.models import Note
from rrg.models import NotePayment
from rrg.models import Payroll
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
            client_inactive = Client(name='weekly-inactive', active=False,
                                     terms=30)
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
            self.session.bulk_save_objects([ClientCheck(client_id=clients[0].id, amount=100, date=dt.now())])
            self.session.bulk_save_objects([ClientCheck(client_id=clients[1].id, amount=100, date=dt.now())])

            objects = []
            for i in invoices:
                i.invoice_items[0].quantity = 12
                i.invoice_items[1].quantity = 24
                logger.debug(i)
                checks = [r for r in self.session.query(ClientCheck).filter(ClientCheck.client == i.contract.client)]
                logger.debug('DEBUGCHECKS')
                logger.debug(checks)
                objects.append(InvoicePayment(amount=6.0, invoice_id=i.id, check_id=checks[0].id))

            self.session.bulk_save_objects(objects)
            epay0 = EmployeePayment(employee_id=employees[0].id, amount=1.0, date=dt.now(), invoice_id=invoices[0].id,
                                    payroll_id=payrolls[0].id)
            epay1 = EmployeePayment(employee_id=employees[1].id, amount=2.0, date=dt.now(), invoice_id=invoices[1].id,
                                    payroll_id=payrolls[0].id)
            objects = [epay0, epay1]
            self.session.bulk_save_objects(objects)

            note0 = Note(employee_id=employees[0].id, amount=1.0)
            note1 = Note(employee_id=employees[1].id, amount=2.0)
            objects = [note0, note1]
            self.session.bulk_save_objects(objects)
            notepayment0 = NotePayment(employee_id=employees[0].id, amount=1.0)
            notepayment1 = NotePayment(employee_id=employees[1].id, amount=2.0)
            objects = [notepayment0, notepayment1]
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

    def test_client_to_xml(self):
        """
        test to_xml() of client
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
        assert 2 == self.session.query(Note).count()
        assert 2 == self.session.query(NotePayment).count()
        assert 12 == self.session.query(InvoicePayment).count()

        cl = self.session.query(Client)[0]
        doc = cl.to_xml()
        logger.debug('XMLCLIENT')
        logger.debug(ET.tostring(doc))
        assert 'weekly' == doc.findall('name')[0].text
        assert 1 == len(doc.findall('checks/check'))
        assert 1 == len(doc.findall('memos/memo'))
        assert 0 == len(doc.findall('contracts/contract'))
        assert 0 == len(doc.findall('contracts/contract/invoices/invoice'))
        assert 0 == len(doc.findall('contracts/contract/contract-items/contract-item'))
        assert 0 == len(doc.findall('contracts/contract/invoices/invoice/invoice-items/invoice-item'))
        assert 0 == len(doc.findall('contracts/contract/invoices/invoice/invoice-items/invoice-item/commissions-items'))
        assert 0 == len(doc.findall('contracts/contract/invoices/invoice/invoice-items/invoice-item/commissions-items/invoices-items-commissions-item'))


        client_collected_baseline = """<client><id>2963</id><name>weekly</name><street1 /><street2 /><state_id>None</state_id><zip /><terms>30</terms><active>True</active><checks><check><id>2913</id><client_id>2963</client_id><number>None</number><amount>100.0</amount><notes>None</notes><date>2016-08-08-00-00-00</date></check></checks><memos><memo><id>761</id><client_id>2963</client_id><notes>cl1 memo</notes><date>2016-08-08-00-00-00</date></memo></memos><contracts><contract><id>17773</id><title>weekly-active-client-active-employee</title><notes /><client_id>2963</client_id><employee_id>6516</employee_id><period_id>1</period_id><active>True</active><terms>30</terms><startdate>2016-07-01-00-00-00</startdate><enddate>2016-09-11-15-53-00</enddate><invoices><invoice><id>17883</id><contract_id>17773</contract_id><date>2016-08-08-00-00-00</date><po>None</po><employerexpenserate>0.1</employerexpenserate><terms>30</terms><timecard>False</timecard><notes>None</notes><period_start>2016-07-11-00-00-00</period_start><period_end>2016-07-17-00-00-00</period_end><posted>False</posted><cleared>False</cleared><voided>False</voided><prcleared>False</prcleared><message>Thank you for your business!</message><amount>600.0</amount><created_date>2016-08-08-00-00-00</created_date><modified_date>2016-08-08-00-00-00</modified_date><created_user_id>None</created_user_id><modified_user_id>None</modified_user_id><due_date>2016-09-07-00-00-00</due_date><date_generated>2016-09-11-15-53-00</date_generated><invoice-items><invoice-item><id>32795</id><invoice_id>17883</invoice_id><description>Regular</description><amount>10.0</amount><cost>5.0</cost><quantity>12.0</quantity><cleared>False</cleared><commissions-items><invoices-items-commissions-item><id>187565</id><invoice_id>17883</invoice_id><employee_id>6518</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person1</employee_lastname><invoices_item_id>32795</invoices_item_id><description>2016-07-11-2016-07-17 Regular</description><date>2016-08-08-00-00-00</date><percent>38.5</percent><amount>20.79</amount><rel_inv_amt>None</rel_inv_amt><rel_inv_line_item_amt>None</rel_inv_line_item_amt><rel_item_amt>None</rel_item_amt><rel_item_quantity>None</rel_item_quantity><rel_item_cost>None</rel_item_cost><rel_item_amt>None</rel_item_amt><cleared>0.0</cleared><voided>None</voided><date_generated>2016-09-11-15-53-00</date_generated><created_date>2016-08-08-00-00-00</created_date><modified_date>2016-08-08-00-00-00</modified_date><created_user_id>2</created_user_id><modified_user_id>2</modified_user_id></invoices-items-commissions-item><invoices-items-commissions-item><id>187566</id><invoice_id>17883</invoice_id><employee_id>6519</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person2</employee_lastname><invoices_item_id>32795</invoices_item_id><description>2016-07-11-2016-07-17 Regular</description><date>2016-08-08-00-00-00</date><percent>61.5</percent><amount>33.21</amount><rel_inv_amt>None</rel_inv_amt><rel_inv_line_item_amt>None</rel_inv_line_item_amt><rel_item_amt>None</rel_item_amt><rel_item_quantity>None</rel_item_quantity><rel_item_cost>None</rel_item_cost><rel_item_amt>None</rel_item_amt><cleared>0.0</cleared><voided>None</voided><date_generated>2016-09-11-15-53-00</date_generated><created_date>2016-08-08-00-00-00</created_date><modified_date>2016-08-08-00-00-00</modified_date><created_user_id>2</created_user_id><modified_user_id>2</modified_user_id></invoices-items-commissions-item></commissions-items></invoice-item><invoice-item><id>32796</id><invoice_id>17883</invoice_id><description>Double Time</description><amount>20.0</amount><cost>10.0</cost><quantity>24.0</quantity><cleared>False</cleared><commissions-items><invoices-items-commissions-item><id>187567</id><invoice_id>17883</invoice_id><employee_id>6518</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person1</employee_lastname><invoices_item_id>32796</invoices_item_id><description>2016-07-11-2016-07-17 Double Time</description><date>2016-08-08-00-00-00</date><percent>38.5</percent><amount>83.16</amount><rel_inv_amt>None</rel_inv_amt><rel_inv_line_item_amt>None</rel_inv_line_item_amt><rel_item_amt>None</rel_item_amt><rel_item_quantity>None</rel_item_quantity><rel_item_cost>None</rel_item_cost><rel_item_amt>None</rel_item_amt><cleared>0.0</cleared><voided>None</voided><date_generated>2016-09-11-15-53-00</date_generated><created_date>2016-08-08-00-00-00</created_date><modified_date>2016-08-08-00-00-00</modified_date><created_user_id>2</created_user_id><modified_user_id>2</modified_user_id></invoices-items-commissions-item><invoices-items-commissions-item><id>187568</id><invoice_id>17883</invoice_id><employee_id>6519</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person2</employee_lastname><invoices_item_id>32796</invoices_item_id><description>2016-07-11-2016-07-17 Double Time</description><date>2016-08-08-00-00-00</date><percent>61.5</percent><amount>132.84</amount><rel_inv_amt>None</rel_inv_amt><rel_inv_line_item_amt>None</rel_inv_line_item_amt><rel_item_amt>None</rel_item_amt><rel_item_quantity>None</rel_item_quantity><rel_item_cost>None</rel_item_cost><rel_item_amt>None</rel_item_amt><cleared>0.0</cleared><voided>None</voided><date_generated>2016-09-11-15-53-00</date_generated><created_date>2016-08-08-00-00-00</created_date><modified_date>2016-08-08-00-00-00</modified_date><created_user_id>2</created_user_id><modified_user_id>2</modified_user_id></invoices-items-commissions-item></commissions-items></invoice-item></invoice-items><invoice-payments><invoice-payment><id>2773</id><invoice_id>17883</invoice_id><check_id>2913</check_id><amount>6.0</amount><notes>None</notes></invoice-payment></invoice-payments><employee-payments><employee-payment><id>745</id><employee_id>6516</employee_id><invoice_id>17883</invoice_id><payroll_id>381</payroll_id><notes /><date>2016-08-08-00-00-00</date><amount>1.0</amount></employee-payment></employee-payments></invoice></invoices><contract-items><contract-item><id>32795</id><active>True</active><contract_id>17773</contract_id><amt>10.0</amt><cost>5.0</cost><description>Regular</description><notes /><contract-commissions-items><contract-item><id>185161</id><employee_id>6518</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person1</employee_lastname><contract_item_id>32795</contract_item_id><percent>38.5</percent></contract-item><contract-item><id>185162</id><employee_id>6519</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person2</employee_lastname><contract_item_id>32795</contract_item_id><percent>61.5</percent></contract-item></contract-commissions-items></contract-item><contract-item><id>32796</id><active>True</active><contract_id>17773</contract_id><amt>20.0</amt><cost>10.0</cost><description>Double Time</description><notes /><contract-commissions-items><contract-item><id>185163</id><employee_id>6518</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person1</employee_lastname><contract_item_id>32796</contract_item_id><percent>38.5</percent></contract-item><contract-item><id>185164</id><employee_id>6519</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person2</employee_lastname><contract_item_id>32796</contract_item_id><percent>61.5</percent></contract-item></contract-commissions-items></contract-item></contract-items></contract><contract><id>17774</id><title>biweekly-active-client-active-employee</title><notes /><client_id>2963</client_id><employee_id>6516</employee_id><period_id>5</period_id><active>True</active><terms>30</terms><startdate>2016-07-01-00-00-00</startdate><enddate>2016-09-11-15-53-00</enddate><invoices><invoice><id>17886</id><contract_id>17774</contract_id><date>2016-08-08-00-00-00</date><po>None</po><employerexpenserate>0.1</employerexpenserate><terms>30</terms><timecard>False</timecard><notes>None</notes><period_start>2016-07-11-00-00-00</period_start><period_end>2016-07-24-00-00-00</period_end><posted>False</posted><cleared>False</cleared><voided>False</voided><prcleared>False</prcleared><message>Thank you for your business!</message><amount>600.0</amount><created_date>2016-08-08-00-00-00</created_date><modified_date>2016-08-08-00-00-00</modified_date><created_user_id>None</created_user_id><modified_user_id>None</modified_user_id><due_date>2016-09-07-00-00-00</due_date><date_generated>2016-09-11-15-53-00</date_generated><invoice-items><invoice-item><id>32801</id><invoice_id>17886</invoice_id><description>Regular</description><amount>10.0</amount><cost>5.0</cost><quantity>12.0</quantity><cleared>False</cleared><commissions-items><invoices-items-commissions-item><id>187577</id><invoice_id>17886</invoice_id><employee_id>6518</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person1</employee_lastname><invoices_item_id>32801</invoices_item_id><description>2016-07-11-2016-07-24 Regular</description><date>2016-08-08-00-00-00</date><percent>38.5</percent><amount>20.79</amount><rel_inv_amt>None</rel_inv_amt><rel_inv_line_item_amt>None</rel_inv_line_item_amt><rel_item_amt>None</rel_item_amt><rel_item_quantity>None</rel_item_quantity><rel_item_cost>None</rel_item_cost><rel_item_amt>None</rel_item_amt><cleared>0.0</cleared><voided>None</voided><date_generated>2016-09-11-15-53-00</date_generated><created_date>2016-08-08-00-00-00</created_date><modified_date>2016-08-08-00-00-00</modified_date><created_user_id>2</created_user_id><modified_user_id>2</modified_user_id></invoices-items-commissions-item><invoices-items-commissions-item><id>187578</id><invoice_id>17886</invoice_id><employee_id>6519</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person2</employee_lastname><invoices_item_id>32801</invoices_item_id><description>2016-07-11-2016-07-24 Regular</description><date>2016-08-08-00-00-00</date><percent>61.5</percent><amount>33.21</amount><rel_inv_amt>None</rel_inv_amt><rel_inv_line_item_amt>None</rel_inv_line_item_amt><rel_item_amt>None</rel_item_amt><rel_item_quantity>None</rel_item_quantity><rel_item_cost>None</rel_item_cost><rel_item_amt>None</rel_item_amt><cleared>0.0</cleared><voided>None</voided><date_generated>2016-09-11-15-53-00</date_generated><created_date>2016-08-08-00-00-00</created_date><modified_date>2016-08-08-00-00-00</modified_date><created_user_id>2</created_user_id><modified_user_id>2</modified_user_id></invoices-items-commissions-item></commissions-items></invoice-item><invoice-item><id>32802</id><invoice_id>17886</invoice_id><description>Double Time</description><amount>20.0</amount><cost>10.0</cost><quantity>24.0</quantity><cleared>False</cleared><commissions-items><invoices-items-commissions-item><id>187579</id><invoice_id>17886</invoice_id><employee_id>6518</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person1</employee_lastname><invoices_item_id>32802</invoices_item_id><description>2016-07-11-2016-07-24 Double Time</description><date>2016-08-08-00-00-00</date><percent>38.5</percent><amount>83.16</amount><rel_inv_amt>None</rel_inv_amt><rel_inv_line_item_amt>None</rel_inv_line_item_amt><rel_item_amt>None</rel_item_amt><rel_item_quantity>None</rel_item_quantity><rel_item_cost>None</rel_item_cost><rel_item_amt>None</rel_item_amt><cleared>0.0</cleared><voided>None</voided><date_generated>2016-09-11-15-53-00</date_generated><created_date>2016-08-08-00-00-00</created_date><modified_date>2016-08-08-00-00-00</modified_date><created_user_id>2</created_user_id><modified_user_id>2</modified_user_id></invoices-items-commissions-item><invoices-items-commissions-item><id>187580</id><invoice_id>17886</invoice_id><employee_id>6519</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person2</employee_lastname><invoices_item_id>32802</invoices_item_id><description>2016-07-11-2016-07-24 Double Time</description><date>2016-08-08-00-00-00</date><percent>61.5</percent><amount>132.84</amount><rel_inv_amt>None</rel_inv_amt><rel_inv_line_item_amt>None</rel_inv_line_item_amt><rel_item_amt>None</rel_item_amt><rel_item_quantity>None</rel_item_quantity><rel_item_cost>None</rel_item_cost><rel_item_amt>None</rel_item_amt><cleared>0.0</cleared><voided>None</voided><date_generated>2016-09-11-15-53-00</date_generated><created_date>2016-08-08-00-00-00</created_date><modified_date>2016-08-08-00-00-00</modified_date><created_user_id>2</created_user_id><modified_user_id>2</modified_user_id></invoices-items-commissions-item></commissions-items></invoice-item></invoice-items><invoice-payments><invoice-payment><id>2776</id><invoice_id>17886</invoice_id><check_id>2913</check_id><amount>6.0</amount><notes>None</notes></invoice-payment></invoice-payments><employee-payments /></invoice></invoices><contract-items><contract-item><id>32797</id><active>True</active><contract_id>17774</contract_id><amt>10.0</amt><cost>5.0</cost><description>Regular</description><notes /><contract-commissions-items><contract-item><id>185165</id><employee_id>6518</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person1</employee_lastname><contract_item_id>32797</contract_item_id><percent>38.5</percent></contract-item><contract-item><id>185166</id><employee_id>6519</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person2</employee_lastname><contract_item_id>32797</contract_item_id><percent>61.5</percent></contract-item></contract-commissions-items></contract-item><contract-item><id>32798</id><active>True</active><contract_id>17774</contract_id><amt>20.0</amt><cost>10.0</cost><description>Double Time</description><notes /><contract-commissions-items><contract-item><id>185167</id><employee_id>6518</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person1</employee_lastname><contract_item_id>32798</contract_item_id><percent>38.5</percent></contract-item><contract-item><id>185168</id><employee_id>6519</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person2</employee_lastname><contract_item_id>32798</contract_item_id><percent>61.5</percent></contract-item></contract-commissions-items></contract-item></contract-items></contract><contract><id>17775</id><title>semimonthly-active-client-active-employee</title><notes /><client_id>2963</client_id><employee_id>6516</employee_id><period_id>2</period_id><active>True</active><terms>30</terms><startdate>2016-07-01-00-00-00</startdate><enddate>2016-09-11-15-53-00</enddate><invoices><invoice><id>17889</id><contract_id>17775</contract_id><date>2016-08-08-00-00-00</date><po>None</po><employerexpenserate>0.1</employerexpenserate><terms>30</terms><timecard>False</timecard><notes>None</notes><period_start>2016-07-16-00-00-00</period_start><period_end>2016-07-31-00-00-00</period_end><posted>False</posted><cleared>False</cleared><voided>False</voided><prcleared>False</prcleared><message>Thank you for your business!</message><amount>600.0</amount><created_date>2016-08-08-00-00-00</created_date><modified_date>2016-08-08-00-00-00</modified_date><created_user_id>None</created_user_id><modified_user_id>None</modified_user_id><due_date>2016-09-07-00-00-00</due_date><date_generated>2016-09-11-15-53-00</date_generated><invoice-items><invoice-item><id>32807</id><invoice_id>17889</invoice_id><description>Regular</description><amount>10.0</amount><cost>5.0</cost><quantity>12.0</quantity><cleared>False</cleared><commissions-items><invoices-items-commissions-item><id>187589</id><invoice_id>17889</invoice_id><employee_id>6518</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person1</employee_lastname><invoices_item_id>32807</invoices_item_id><description>2016-07-16-2016-07-31 Regular</description><date>2016-08-08-00-00-00</date><percent>38.5</percent><amount>20.79</amount><rel_inv_amt>None</rel_inv_amt><rel_inv_line_item_amt>None</rel_inv_line_item_amt><rel_item_amt>None</rel_item_amt><rel_item_quantity>None</rel_item_quantity><rel_item_cost>None</rel_item_cost><rel_item_amt>None</rel_item_amt><cleared>0.0</cleared><voided>None</voided><date_generated>2016-09-11-15-53-00</date_generated><created_date>2016-08-08-00-00-00</created_date><modified_date>2016-08-08-00-00-00</modified_date><created_user_id>2</created_user_id><modified_user_id>2</modified_user_id></invoices-items-commissions-item><invoices-items-commissions-item><id>187590</id><invoice_id>17889</invoice_id><employee_id>6519</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person2</employee_lastname><invoices_item_id>32807</invoices_item_id><description>2016-07-16-2016-07-31 Regular</description><date>2016-08-08-00-00-00</date><percent>61.5</percent><amount>33.21</amount><rel_inv_amt>None</rel_inv_amt><rel_inv_line_item_amt>None</rel_inv_line_item_amt><rel_item_amt>None</rel_item_amt><rel_item_quantity>None</rel_item_quantity><rel_item_cost>None</rel_item_cost><rel_item_amt>None</rel_item_amt><cleared>0.0</cleared><voided>None</voided><date_generated>2016-09-11-15-53-00</date_generated><created_date>2016-08-08-00-00-00</created_date><modified_date>2016-08-08-00-00-00</modified_date><created_user_id>2</created_user_id><modified_user_id>2</modified_user_id></invoices-items-commissions-item></commissions-items></invoice-item><invoice-item><id>32808</id><invoice_id>17889</invoice_id><description>Double Time</description><amount>20.0</amount><cost>10.0</cost><quantity>24.0</quantity><cleared>False</cleared><commissions-items><invoices-items-commissions-item><id>187591</id><invoice_id>17889</invoice_id><employee_id>6518</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person1</employee_lastname><invoices_item_id>32808</invoices_item_id><description>2016-07-16-2016-07-31 Double Time</description><date>2016-08-08-00-00-00</date><percent>38.5</percent><amount>83.16</amount><rel_inv_amt>None</rel_inv_amt><rel_inv_line_item_amt>None</rel_inv_line_item_amt><rel_item_amt>None</rel_item_amt><rel_item_quantity>None</rel_item_quantity><rel_item_cost>None</rel_item_cost><rel_item_amt>None</rel_item_amt><cleared>0.0</cleared><voided>None</voided><date_generated>2016-09-11-15-53-00</date_generated><created_date>2016-08-08-00-00-00</created_date><modified_date>2016-08-08-00-00-00</modified_date><created_user_id>2</created_user_id><modified_user_id>2</modified_user_id></invoices-items-commissions-item><invoices-items-commissions-item><id>187592</id><invoice_id>17889</invoice_id><employee_id>6519</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person2</employee_lastname><invoices_item_id>32808</invoices_item_id><description>2016-07-16-2016-07-31 Double Time</description><date>2016-08-08-00-00-00</date><percent>61.5</percent><amount>132.84</amount><rel_inv_amt>None</rel_inv_amt><rel_inv_line_item_amt>None</rel_inv_line_item_amt><rel_item_amt>None</rel_item_amt><rel_item_quantity>None</rel_item_quantity><rel_item_cost>None</rel_item_cost><rel_item_amt>None</rel_item_amt><cleared>0.0</cleared><voided>None</voided><date_generated>2016-09-11-15-53-00</date_generated><created_date>2016-08-08-00-00-00</created_date><modified_date>2016-08-08-00-00-00</modified_date><created_user_id>2</created_user_id><modified_user_id>2</modified_user_id></invoices-items-commissions-item></commissions-items></invoice-item></invoice-items><invoice-payments><invoice-payment><id>2779</id><invoice_id>17889</invoice_id><check_id>2913</check_id><amount>6.0</amount><notes>None</notes></invoice-payment></invoice-payments><employee-payments /></invoice></invoices><contract-items><contract-item><id>32799</id><active>True</active><contract_id>17775</contract_id><amt>10.0</amt><cost>5.0</cost><description>Regular</description><notes /><contract-commissions-items><contract-item><id>185169</id><employee_id>6518</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person1</employee_lastname><contract_item_id>32799</contract_item_id><percent>38.5</percent></contract-item><contract-item><id>185170</id><employee_id>6519</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person2</employee_lastname><contract_item_id>32799</contract_item_id><percent>61.5</percent></contract-item></contract-commissions-items></contract-item><contract-item><id>32800</id><active>True</active><contract_id>17775</contract_id><amt>20.0</amt><cost>10.0</cost><description>Double Time</description><notes /><contract-commissions-items><contract-item><id>185171</id><employee_id>6518</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person1</employee_lastname><contract_item_id>32800</contract_item_id><percent>38.5</percent></contract-item><contract-item><id>185172</id><employee_id>6519</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person2</employee_lastname><contract_item_id>32800</contract_item_id><percent>61.5</percent></contract-item></contract-commissions-items></contract-item></contract-items></contract><contract><id>17776</id><title>monthly-active-client-active-employee</title><notes /><client_id>2963</client_id><employee_id>6516</employee_id><period_id>3</period_id><active>True</active><terms>30</terms><startdate>2016-07-01-00-00-00</startdate><enddate>2016-09-11-15-53-00</enddate><invoices><invoice><id>17892</id><contract_id>17776</contract_id><date>2016-08-08-00-00-00</date><po>None</po><employerexpenserate>0.1</employerexpenserate><terms>30</terms><timecard>False</timecard><notes>None</notes><period_start>2016-08-01-00-00-00</period_start><period_end>2016-08-31-00-00-00</period_end><posted>False</posted><cleared>False</cleared><voided>False</voided><prcleared>False</prcleared><message>Thank you for your business!</message><amount>600.0</amount><created_date>2016-08-08-00-00-00</created_date><modified_date>2016-08-08-00-00-00</modified_date><created_user_id>None</created_user_id><modified_user_id>None</modified_user_id><due_date>2016-09-07-00-00-00</due_date><date_generated>2016-09-11-15-53-00</date_generated><invoice-items><invoice-item><id>32813</id><invoice_id>17892</invoice_id><description>Regular</description><amount>10.0</amount><cost>5.0</cost><quantity>12.0</quantity><cleared>False</cleared><commissions-items><invoices-items-commissions-item><id>187601</id><invoice_id>17892</invoice_id><employee_id>6518</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person1</employee_lastname><invoices_item_id>32813</invoices_item_id><description>2016-08-01-2016-08-31 Regular</description><date>2016-08-08-00-00-00</date><percent>38.5</percent><amount>20.79</amount><rel_inv_amt>None</rel_inv_amt><rel_inv_line_item_amt>None</rel_inv_line_item_amt><rel_item_amt>None</rel_item_amt><rel_item_quantity>None</rel_item_quantity><rel_item_cost>None</rel_item_cost><rel_item_amt>None</rel_item_amt><cleared>0.0</cleared><voided>None</voided><date_generated>2016-09-11-15-53-00</date_generated><created_date>2016-08-08-00-00-00</created_date><modified_date>2016-08-08-00-00-00</modified_date><created_user_id>2</created_user_id><modified_user_id>2</modified_user_id></invoices-items-commissions-item><invoices-items-commissions-item><id>187602</id><invoice_id>17892</invoice_id><employee_id>6519</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person2</employee_lastname><invoices_item_id>32813</invoices_item_id><description>2016-08-01-2016-08-31 Regular</description><date>2016-08-08-00-00-00</date><percent>61.5</percent><amount>33.21</amount><rel_inv_amt>None</rel_inv_amt><rel_inv_line_item_amt>None</rel_inv_line_item_amt><rel_item_amt>None</rel_item_amt><rel_item_quantity>None</rel_item_quantity><rel_item_cost>None</rel_item_cost><rel_item_amt>None</rel_item_amt><cleared>0.0</cleared><voided>None</voided><date_generated>2016-09-11-15-53-00</date_generated><created_date>2016-08-08-00-00-00</created_date><modified_date>2016-08-08-00-00-00</modified_date><created_user_id>2</created_user_id><modified_user_id>2</modified_user_id></invoices-items-commissions-item></commissions-items></invoice-item><invoice-item><id>32814</id><invoice_id>17892</invoice_id><description>Double Time</description><amount>20.0</amount><cost>10.0</cost><quantity>24.0</quantity><cleared>False</cleared><commissions-items><invoices-items-commissions-item><id>187603</id><invoice_id>17892</invoice_id><employee_id>6518</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person1</employee_lastname><invoices_item_id>32814</invoices_item_id><description>2016-08-01-2016-08-31 Double Time</description><date>2016-08-08-00-00-00</date><percent>38.5</percent><amount>83.16</amount><rel_inv_amt>None</rel_inv_amt><rel_inv_line_item_amt>None</rel_inv_line_item_amt><rel_item_amt>None</rel_item_amt><rel_item_quantity>None</rel_item_quantity><rel_item_cost>None</rel_item_cost><rel_item_amt>None</rel_item_amt><cleared>0.0</cleared><voided>None</voided><date_generated>2016-09-11-15-53-00</date_generated><created_date>2016-08-08-00-00-00</created_date><modified_date>2016-08-08-00-00-00</modified_date><created_user_id>2</created_user_id><modified_user_id>2</modified_user_id></invoices-items-commissions-item><invoices-items-commissions-item><id>187604</id><invoice_id>17892</invoice_id><employee_id>6519</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person2</employee_lastname><invoices_item_id>32814</invoices_item_id><description>2016-08-01-2016-08-31 Double Time</description><date>2016-08-08-00-00-00</date><percent>61.5</percent><amount>132.84</amount><rel_inv_amt>None</rel_inv_amt><rel_inv_line_item_amt>None</rel_inv_line_item_amt><rel_item_amt>None</rel_item_amt><rel_item_quantity>None</rel_item_quantity><rel_item_cost>None</rel_item_cost><rel_item_amt>None</rel_item_amt><cleared>0.0</cleared><voided>None</voided><date_generated>2016-09-11-15-53-00</date_generated><created_date>2016-08-08-00-00-00</created_date><modified_date>2016-08-08-00-00-00</modified_date><created_user_id>2</created_user_id><modified_user_id>2</modified_user_id></invoices-items-commissions-item></commissions-items></invoice-item></invoice-items><invoice-payments><invoice-payment><id>2782</id><invoice_id>17892</invoice_id><check_id>2913</check_id><amount>6.0</amount><notes>None</notes></invoice-payment></invoice-payments><employee-payments /></invoice></invoices><contract-items><contract-item><id>32801</id><active>True</active><contract_id>17776</contract_id><amt>10.0</amt><cost>5.0</cost><description>Regular</description><notes /><contract-commissions-items><contract-item><id>185173</id><employee_id>6518</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person1</employee_lastname><contract_item_id>32801</contract_item_id><percent>38.5</percent></contract-item><contract-item><id>185174</id><employee_id>6519</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person2</employee_lastname><contract_item_id>32801</contract_item_id><percent>61.5</percent></contract-item></contract-commissions-items></contract-item><contract-item><id>32802</id><active>True</active><contract_id>17776</contract_id><amt>20.0</amt><cost>10.0</cost><description>Double Time</description><notes /><contract-commissions-items><contract-item><id>185175</id><employee_id>6518</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person1</employee_lastname><contract_item_id>32802</contract_item_id><percent>38.5</percent></contract-item><contract-item><id>185176</id><employee_id>6519</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person2</employee_lastname><contract_item_id>32802</contract_item_id><percent>61.5</percent></contract-item></contract-commissions-items></contract-item></contract-items></contract></contracts></client>"""

        doc = ET.fromstring(client_collected_baseline)
        assert 'weekly' == doc.findall('name')[0].text
        assert 1 == len(doc.findall('checks/check'))
        assert 1 == len(doc.findall('memos/memo'))
        assert 4 == len(doc.findall('contracts/contract'))
        assert 4 == len(doc.findall('contracts/contract/invoices/invoice'))
        assert 8 == len(doc.findall('contracts/contract/contract-items/contract-item'))
        assert 8 == len(doc.findall('contracts/contract/invoices/invoice/invoice-items/invoice-item'))
        assert 8 == len(doc.findall('contracts/contract/invoices/invoice/invoice-items/invoice-item/commissions-items'))
        assert 16 == len(doc.findall('contracts/contract/invoices/invoice/invoice-items/invoice-item/commissions-items/invoices-items-commissions-item'))


        base_cl_doc = doc
        contracts_subele = doc.findall('contracts')[0]
        cdoc = doc_attach_collected_contracts([i for i in base_cl_doc.findall('contracts/contract')])
        doc.remove(contracts_subele)
        doc.append(cdoc)
        assert 'weekly' == doc.findall('name')[0].text
        assert 1 == len(doc.findall('checks/check'))
        assert 1 == len(doc.findall('memos/memo'))
        assert 4 == len(doc.findall('contracts/contract'))
        assert 4 == len(doc.findall('contracts/contract/invoices/invoice'))
        assert 8 == len(doc.findall('contracts/contract/contract-items/contract-item'))
        assert 8 == len(doc.findall('contracts/contract/invoices/invoice/invoice-items/invoice-item'))
        assert 8 == len(doc.findall('contracts/contract/invoices/invoice/invoice-items/invoice-item/commissions-items'))
        assert 16 == len(doc.findall('contracts/contract/invoices/invoice/invoice-items/invoice-item/commissions-items/invoices-items-commissions-item'))
