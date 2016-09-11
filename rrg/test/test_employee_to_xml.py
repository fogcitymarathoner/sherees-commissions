import sys
from datetime import datetime as dt
from datetime import timedelta as td
import logging
from freezegun import freeze_time
import xml.etree.ElementTree as ET

from rrg.archive import employee_attach_collected_contracts
from rrg.models import Contract
from rrg.models import ContractItem
from rrg.models import ContractItemCommItem
from rrg.models import Client
from rrg.models import ClientMemo
from rrg.models import ClientCheck
from rrg.models import Employee
from rrg.models import EmployeePayment
from rrg.models import EmployeeMemo
from rrg.models import Invoice
from rrg.models import InvoicePayment
from rrg.models import Iitem
from rrg.models import Citem
from rrg.models import Payroll
from rrg.models import periods
from rrg.models import Note
from rrg.models import NotePayment
from rrg.reminders import weeks_between_dates
from rrg.reminders import biweeks_between_dates
from rrg.reminders import semimonths_between_dates
from rrg.reminders import months_between_dates
from rrg.reminders import current_semimonth
from rrg.reminders_generation import create_invoice_for_period

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

    def test_employee_to_xml(self):
        """
        test to_xml() of employee
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

        emp = self.session.query(Employee)[0]
        doc = emp.to_xml()
        logger.debug('XMLEmployee')
        logger.debug(ET.tostring(doc))
        assert 'firstname' == doc.findall('firstname')[0].text
        assert 1 == len(doc.findall('employee-payments/employee-payment'))
        assert 1 == len(doc.findall('memos/memo'))
        assert 0 == len(doc.findall('contracts/contract'))
        assert 0 == len(doc.findall('contracts/contract/invoices/invoice'))
        assert 0 == len(doc.findall('contracts/contract/contract-items/contract-item'))
        assert 0 == len(doc.findall('contracts/contract/invoices/invoice/invoice-items/invoice-item'))
        assert 0 == len(doc.findall('contracts/contract/invoices/invoice/invoice-items/invoice-item/commissions-items'))
        assert 0 == len(doc.findall('contracts/contract/invoices/invoice/invoice-items/invoice-item/commissions-items/invoices-items-commissions-item'))
        original_saved_emp = doc
        employee_collected_base = """<employee><id>6520</id><firstname>firstname</firstname><lastname>activelastname</lastname><mi /><nickname /><street1 /><street2 /><state_id>None</state_id><zip /><ssn_crypto /><bankaccountnumber_crypto /><bankaccounttype /><bankroutingnumber_crypto /><directdeposit>None</directdeposit><allowancefederal>None</allowancefederal><allowancestate>None</allowancestate><extradeductionfed>None</extradeductionfed><extradeductionstate>None</extradeductionstate><maritalstatusfed /><maritalstatusstate /><usworkstatus>None</usworkstatus><notes /><state_id>None</state_id><salesforce>None</salesforce><active>True</active><tcard>None</tcard><w4>None</w4><de34>None</de34><i9>None</i9><medical>None</medical><voided>None</voided><indust>None</indust><info>None</info><phone /><dob>2016-09-11-15-53-00</dob><startdate>2016-09-11-15-53-00</startdate><enddate>2016-09-11-15-53-00</enddate><employee-payments><employee-payment><id>747</id><employee_id>6520</employee_id><invoice_id>17895</invoice_id><payroll_id>382</payroll_id><notes /><date>2016-08-08-00-00-00</date><amount>1.0</amount></employee-payment></employee-payments><memos><memo><id>1525</id><employee_id>6520</employee_id><notes>emp1 memo</notes><date>2016-08-08-00-00-00</date></memo></memos><contracts><contract><id>17785</id><title>weekly-active-client-active-employee</title><notes /><client_id>2965</client_id><employee_id>6520</employee_id><period_id>1</period_id><active>True</active><terms>30</terms><startdate>2016-07-01-00-00-00</startdate><enddate>2016-09-11-15-53-00</enddate><invoices><invoice><id>17895</id><contract_id>17785</contract_id><date>2016-08-08-00-00-00</date><po>None</po><employerexpenserate>0.1</employerexpenserate><terms>30</terms><timecard>False</timecard><notes>None</notes><period_start>2016-07-11-00-00-00</period_start><period_end>2016-07-17-00-00-00</period_end><posted>False</posted><cleared>False</cleared><voided>False</voided><prcleared>False</prcleared><message>Thank you for your business!</message><amount>600.0</amount><created_date>2016-08-08-00-00-00</created_date><modified_date>2016-08-08-00-00-00</modified_date><created_user_id>None</created_user_id><modified_user_id>None</modified_user_id><due_date>2016-09-07-00-00-00</due_date><date_generated>2016-09-11-15-53-00</date_generated><invoice-items><invoice-item><id>32819</id><invoice_id>17895</invoice_id><description>Regular</description><amount>10.0</amount><cost>5.0</cost><quantity>12.0</quantity><cleared>False</cleared><commissions-items><invoices-items-commissions-item><id>187613</id><invoice_id>17895</invoice_id><employee_id>6522</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person1</employee_lastname><invoices_item_id>32819</invoices_item_id><description>2016-07-11-2016-07-17 Regular</description><date>2016-08-08-00-00-00</date><percent>38.5</percent><amount>20.79</amount><rel_inv_amt>None</rel_inv_amt><rel_inv_line_item_amt>None</rel_inv_line_item_amt><rel_item_amt>None</rel_item_amt><rel_item_quantity>None</rel_item_quantity><rel_item_cost>None</rel_item_cost><rel_item_amt>None</rel_item_amt><cleared>0.0</cleared><voided>None</voided><date_generated>2016-09-11-15-53-00</date_generated><created_date>2016-08-08-00-00-00</created_date><modified_date>2016-08-08-00-00-00</modified_date><created_user_id>2</created_user_id><modified_user_id>2</modified_user_id></invoices-items-commissions-item><invoices-items-commissions-item><id>187614</id><invoice_id>17895</invoice_id><employee_id>6523</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person2</employee_lastname><invoices_item_id>32819</invoices_item_id><description>2016-07-11-2016-07-17 Regular</description><date>2016-08-08-00-00-00</date><percent>61.5</percent><amount>33.21</amount><rel_inv_amt>None</rel_inv_amt><rel_inv_line_item_amt>None</rel_inv_line_item_amt><rel_item_amt>None</rel_item_amt><rel_item_quantity>None</rel_item_quantity><rel_item_cost>None</rel_item_cost><rel_item_amt>None</rel_item_amt><cleared>0.0</cleared><voided>None</voided><date_generated>2016-09-11-15-53-00</date_generated><created_date>2016-08-08-00-00-00</created_date><modified_date>2016-08-08-00-00-00</modified_date><created_user_id>2</created_user_id><modified_user_id>2</modified_user_id></invoices-items-commissions-item></commissions-items></invoice-item><invoice-item><id>32820</id><invoice_id>17895</invoice_id><description>Double Time</description><amount>20.0</amount><cost>10.0</cost><quantity>24.0</quantity><cleared>False</cleared><commissions-items><invoices-items-commissions-item><id>187615</id><invoice_id>17895</invoice_id><employee_id>6522</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person1</employee_lastname><invoices_item_id>32820</invoices_item_id><description>2016-07-11-2016-07-17 Double Time</description><date>2016-08-08-00-00-00</date><percent>38.5</percent><amount>83.16</amount><rel_inv_amt>None</rel_inv_amt><rel_inv_line_item_amt>None</rel_inv_line_item_amt><rel_item_amt>None</rel_item_amt><rel_item_quantity>None</rel_item_quantity><rel_item_cost>None</rel_item_cost><rel_item_amt>None</rel_item_amt><cleared>0.0</cleared><voided>None</voided><date_generated>2016-09-11-15-53-00</date_generated><created_date>2016-08-08-00-00-00</created_date><modified_date>2016-08-08-00-00-00</modified_date><created_user_id>2</created_user_id><modified_user_id>2</modified_user_id></invoices-items-commissions-item><invoices-items-commissions-item><id>187616</id><invoice_id>17895</invoice_id><employee_id>6523</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person2</employee_lastname><invoices_item_id>32820</invoices_item_id><description>2016-07-11-2016-07-17 Double Time</description><date>2016-08-08-00-00-00</date><percent>61.5</percent><amount>132.84</amount><rel_inv_amt>None</rel_inv_amt><rel_inv_line_item_amt>None</rel_inv_line_item_amt><rel_item_amt>None</rel_item_amt><rel_item_quantity>None</rel_item_quantity><rel_item_cost>None</rel_item_cost><rel_item_amt>None</rel_item_amt><cleared>0.0</cleared><voided>None</voided><date_generated>2016-09-11-15-53-00</date_generated><created_date>2016-08-08-00-00-00</created_date><modified_date>2016-08-08-00-00-00</modified_date><created_user_id>2</created_user_id><modified_user_id>2</modified_user_id></invoices-items-commissions-item></commissions-items></invoice-item></invoice-items><invoice-payments><invoice-payment><id>2785</id><invoice_id>17895</invoice_id><check_id>2915</check_id><amount>6.0</amount><notes>None</notes></invoice-payment></invoice-payments><employee-payments><employee-payment><id>747</id><employee_id>6520</employee_id><invoice_id>17895</invoice_id><payroll_id>382</payroll_id><notes /><date>2016-08-08-00-00-00</date><amount>1.0</amount></employee-payment></employee-payments></invoice></invoices><contract-items><contract-item><id>32819</id><active>True</active><contract_id>17785</contract_id><amt>10.0</amt><cost>5.0</cost><description>Regular</description><notes /><contract-commissions-items><contract-item><id>185209</id><employee_id>6522</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person1</employee_lastname><contract_item_id>32819</contract_item_id><percent>38.5</percent></contract-item><contract-item><id>185210</id><employee_id>6523</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person2</employee_lastname><contract_item_id>32819</contract_item_id><percent>61.5</percent></contract-item></contract-commissions-items></contract-item><contract-item><id>32820</id><active>True</active><contract_id>17785</contract_id><amt>20.0</amt><cost>10.0</cost><description>Double Time</description><notes /><contract-commissions-items><contract-item><id>185211</id><employee_id>6522</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person1</employee_lastname><contract_item_id>32820</contract_item_id><percent>38.5</percent></contract-item><contract-item><id>185212</id><employee_id>6523</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person2</employee_lastname><contract_item_id>32820</contract_item_id><percent>61.5</percent></contract-item></contract-commissions-items></contract-item></contract-items></contract><contract><id>17786</id><title>biweekly-active-client-active-employee</title><notes /><client_id>2965</client_id><employee_id>6520</employee_id><period_id>5</period_id><active>True</active><terms>30</terms><startdate>2016-07-01-00-00-00</startdate><enddate>2016-09-11-15-53-00</enddate><invoices><invoice><id>17898</id><contract_id>17786</contract_id><date>2016-08-08-00-00-00</date><po>None</po><employerexpenserate>0.1</employerexpenserate><terms>30</terms><timecard>False</timecard><notes>None</notes><period_start>2016-07-11-00-00-00</period_start><period_end>2016-07-24-00-00-00</period_end><posted>False</posted><cleared>False</cleared><voided>False</voided><prcleared>False</prcleared><message>Thank you for your business!</message><amount>600.0</amount><created_date>2016-08-08-00-00-00</created_date><modified_date>2016-08-08-00-00-00</modified_date><created_user_id>None</created_user_id><modified_user_id>None</modified_user_id><due_date>2016-09-07-00-00-00</due_date><date_generated>2016-09-11-15-53-00</date_generated><invoice-items><invoice-item><id>32825</id><invoice_id>17898</invoice_id><description>Regular</description><amount>10.0</amount><cost>5.0</cost><quantity>12.0</quantity><cleared>False</cleared><commissions-items><invoices-items-commissions-item><id>187625</id><invoice_id>17898</invoice_id><employee_id>6522</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person1</employee_lastname><invoices_item_id>32825</invoices_item_id><description>2016-07-11-2016-07-24 Regular</description><date>2016-08-08-00-00-00</date><percent>38.5</percent><amount>20.79</amount><rel_inv_amt>None</rel_inv_amt><rel_inv_line_item_amt>None</rel_inv_line_item_amt><rel_item_amt>None</rel_item_amt><rel_item_quantity>None</rel_item_quantity><rel_item_cost>None</rel_item_cost><rel_item_amt>None</rel_item_amt><cleared>0.0</cleared><voided>None</voided><date_generated>2016-09-11-15-53-00</date_generated><created_date>2016-08-08-00-00-00</created_date><modified_date>2016-08-08-00-00-00</modified_date><created_user_id>2</created_user_id><modified_user_id>2</modified_user_id></invoices-items-commissions-item><invoices-items-commissions-item><id>187626</id><invoice_id>17898</invoice_id><employee_id>6523</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person2</employee_lastname><invoices_item_id>32825</invoices_item_id><description>2016-07-11-2016-07-24 Regular</description><date>2016-08-08-00-00-00</date><percent>61.5</percent><amount>33.21</amount><rel_inv_amt>None</rel_inv_amt><rel_inv_line_item_amt>None</rel_inv_line_item_amt><rel_item_amt>None</rel_item_amt><rel_item_quantity>None</rel_item_quantity><rel_item_cost>None</rel_item_cost><rel_item_amt>None</rel_item_amt><cleared>0.0</cleared><voided>None</voided><date_generated>2016-09-11-15-53-00</date_generated><created_date>2016-08-08-00-00-00</created_date><modified_date>2016-08-08-00-00-00</modified_date><created_user_id>2</created_user_id><modified_user_id>2</modified_user_id></invoices-items-commissions-item></commissions-items></invoice-item><invoice-item><id>32826</id><invoice_id>17898</invoice_id><description>Double Time</description><amount>20.0</amount><cost>10.0</cost><quantity>24.0</quantity><cleared>False</cleared><commissions-items><invoices-items-commissions-item><id>187627</id><invoice_id>17898</invoice_id><employee_id>6522</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person1</employee_lastname><invoices_item_id>32826</invoices_item_id><description>2016-07-11-2016-07-24 Double Time</description><date>2016-08-08-00-00-00</date><percent>38.5</percent><amount>83.16</amount><rel_inv_amt>None</rel_inv_amt><rel_inv_line_item_amt>None</rel_inv_line_item_amt><rel_item_amt>None</rel_item_amt><rel_item_quantity>None</rel_item_quantity><rel_item_cost>None</rel_item_cost><rel_item_amt>None</rel_item_amt><cleared>0.0</cleared><voided>None</voided><date_generated>2016-09-11-15-53-00</date_generated><created_date>2016-08-08-00-00-00</created_date><modified_date>2016-08-08-00-00-00</modified_date><created_user_id>2</created_user_id><modified_user_id>2</modified_user_id></invoices-items-commissions-item><invoices-items-commissions-item><id>187628</id><invoice_id>17898</invoice_id><employee_id>6523</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person2</employee_lastname><invoices_item_id>32826</invoices_item_id><description>2016-07-11-2016-07-24 Double Time</description><date>2016-08-08-00-00-00</date><percent>61.5</percent><amount>132.84</amount><rel_inv_amt>None</rel_inv_amt><rel_inv_line_item_amt>None</rel_inv_line_item_amt><rel_item_amt>None</rel_item_amt><rel_item_quantity>None</rel_item_quantity><rel_item_cost>None</rel_item_cost><rel_item_amt>None</rel_item_amt><cleared>0.0</cleared><voided>None</voided><date_generated>2016-09-11-15-53-00</date_generated><created_date>2016-08-08-00-00-00</created_date><modified_date>2016-08-08-00-00-00</modified_date><created_user_id>2</created_user_id><modified_user_id>2</modified_user_id></invoices-items-commissions-item></commissions-items></invoice-item></invoice-items><invoice-payments><invoice-payment><id>2788</id><invoice_id>17898</invoice_id><check_id>2915</check_id><amount>6.0</amount><notes>None</notes></invoice-payment></invoice-payments><employee-payments /></invoice></invoices><contract-items><contract-item><id>32821</id><active>True</active><contract_id>17786</contract_id><amt>10.0</amt><cost>5.0</cost><description>Regular</description><notes /><contract-commissions-items><contract-item><id>185213</id><employee_id>6522</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person1</employee_lastname><contract_item_id>32821</contract_item_id><percent>38.5</percent></contract-item><contract-item><id>185214</id><employee_id>6523</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person2</employee_lastname><contract_item_id>32821</contract_item_id><percent>61.5</percent></contract-item></contract-commissions-items></contract-item><contract-item><id>32822</id><active>True</active><contract_id>17786</contract_id><amt>20.0</amt><cost>10.0</cost><description>Double Time</description><notes /><contract-commissions-items><contract-item><id>185215</id><employee_id>6522</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person1</employee_lastname><contract_item_id>32822</contract_item_id><percent>38.5</percent></contract-item><contract-item><id>185216</id><employee_id>6523</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person2</employee_lastname><contract_item_id>32822</contract_item_id><percent>61.5</percent></contract-item></contract-commissions-items></contract-item></contract-items></contract><contract><id>17787</id><title>semimonthly-active-client-active-employee</title><notes /><client_id>2965</client_id><employee_id>6520</employee_id><period_id>2</period_id><active>True</active><terms>30</terms><startdate>2016-07-01-00-00-00</startdate><enddate>2016-09-11-15-53-00</enddate><invoices><invoice><id>17901</id><contract_id>17787</contract_id><date>2016-08-08-00-00-00</date><po>None</po><employerexpenserate>0.1</employerexpenserate><terms>30</terms><timecard>False</timecard><notes>None</notes><period_start>2016-07-16-00-00-00</period_start><period_end>2016-07-31-00-00-00</period_end><posted>False</posted><cleared>False</cleared><voided>False</voided><prcleared>False</prcleared><message>Thank you for your business!</message><amount>600.0</amount><created_date>2016-08-08-00-00-00</created_date><modified_date>2016-08-08-00-00-00</modified_date><created_user_id>None</created_user_id><modified_user_id>None</modified_user_id><due_date>2016-09-07-00-00-00</due_date><date_generated>2016-09-11-15-53-00</date_generated><invoice-items><invoice-item><id>32831</id><invoice_id>17901</invoice_id><description>Regular</description><amount>10.0</amount><cost>5.0</cost><quantity>12.0</quantity><cleared>False</cleared><commissions-items><invoices-items-commissions-item><id>187637</id><invoice_id>17901</invoice_id><employee_id>6522</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person1</employee_lastname><invoices_item_id>32831</invoices_item_id><description>2016-07-16-2016-07-31 Regular</description><date>2016-08-08-00-00-00</date><percent>38.5</percent><amount>20.79</amount><rel_inv_amt>None</rel_inv_amt><rel_inv_line_item_amt>None</rel_inv_line_item_amt><rel_item_amt>None</rel_item_amt><rel_item_quantity>None</rel_item_quantity><rel_item_cost>None</rel_item_cost><rel_item_amt>None</rel_item_amt><cleared>0.0</cleared><voided>None</voided><date_generated>2016-09-11-15-53-00</date_generated><created_date>2016-08-08-00-00-00</created_date><modified_date>2016-08-08-00-00-00</modified_date><created_user_id>2</created_user_id><modified_user_id>2</modified_user_id></invoices-items-commissions-item><invoices-items-commissions-item><id>187638</id><invoice_id>17901</invoice_id><employee_id>6523</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person2</employee_lastname><invoices_item_id>32831</invoices_item_id><description>2016-07-16-2016-07-31 Regular</description><date>2016-08-08-00-00-00</date><percent>61.5</percent><amount>33.21</amount><rel_inv_amt>None</rel_inv_amt><rel_inv_line_item_amt>None</rel_inv_line_item_amt><rel_item_amt>None</rel_item_amt><rel_item_quantity>None</rel_item_quantity><rel_item_cost>None</rel_item_cost><rel_item_amt>None</rel_item_amt><cleared>0.0</cleared><voided>None</voided><date_generated>2016-09-11-15-53-00</date_generated><created_date>2016-08-08-00-00-00</created_date><modified_date>2016-08-08-00-00-00</modified_date><created_user_id>2</created_user_id><modified_user_id>2</modified_user_id></invoices-items-commissions-item></commissions-items></invoice-item><invoice-item><id>32832</id><invoice_id>17901</invoice_id><description>Double Time</description><amount>20.0</amount><cost>10.0</cost><quantity>24.0</quantity><cleared>False</cleared><commissions-items><invoices-items-commissions-item><id>187639</id><invoice_id>17901</invoice_id><employee_id>6522</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person1</employee_lastname><invoices_item_id>32832</invoices_item_id><description>2016-07-16-2016-07-31 Double Time</description><date>2016-08-08-00-00-00</date><percent>38.5</percent><amount>83.16</amount><rel_inv_amt>None</rel_inv_amt><rel_inv_line_item_amt>None</rel_inv_line_item_amt><rel_item_amt>None</rel_item_amt><rel_item_quantity>None</rel_item_quantity><rel_item_cost>None</rel_item_cost><rel_item_amt>None</rel_item_amt><cleared>0.0</cleared><voided>None</voided><date_generated>2016-09-11-15-53-00</date_generated><created_date>2016-08-08-00-00-00</created_date><modified_date>2016-08-08-00-00-00</modified_date><created_user_id>2</created_user_id><modified_user_id>2</modified_user_id></invoices-items-commissions-item><invoices-items-commissions-item><id>187640</id><invoice_id>17901</invoice_id><employee_id>6523</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person2</employee_lastname><invoices_item_id>32832</invoices_item_id><description>2016-07-16-2016-07-31 Double Time</description><date>2016-08-08-00-00-00</date><percent>61.5</percent><amount>132.84</amount><rel_inv_amt>None</rel_inv_amt><rel_inv_line_item_amt>None</rel_inv_line_item_amt><rel_item_amt>None</rel_item_amt><rel_item_quantity>None</rel_item_quantity><rel_item_cost>None</rel_item_cost><rel_item_amt>None</rel_item_amt><cleared>0.0</cleared><voided>None</voided><date_generated>2016-09-11-15-53-00</date_generated><created_date>2016-08-08-00-00-00</created_date><modified_date>2016-08-08-00-00-00</modified_date><created_user_id>2</created_user_id><modified_user_id>2</modified_user_id></invoices-items-commissions-item></commissions-items></invoice-item></invoice-items><invoice-payments><invoice-payment><id>2791</id><invoice_id>17901</invoice_id><check_id>2915</check_id><amount>6.0</amount><notes>None</notes></invoice-payment></invoice-payments><employee-payments /></invoice></invoices><contract-items><contract-item><id>32823</id><active>True</active><contract_id>17787</contract_id><amt>10.0</amt><cost>5.0</cost><description>Regular</description><notes /><contract-commissions-items><contract-item><id>185217</id><employee_id>6522</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person1</employee_lastname><contract_item_id>32823</contract_item_id><percent>38.5</percent></contract-item><contract-item><id>185218</id><employee_id>6523</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person2</employee_lastname><contract_item_id>32823</contract_item_id><percent>61.5</percent></contract-item></contract-commissions-items></contract-item><contract-item><id>32824</id><active>True</active><contract_id>17787</contract_id><amt>20.0</amt><cost>10.0</cost><description>Double Time</description><notes /><contract-commissions-items><contract-item><id>185219</id><employee_id>6522</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person1</employee_lastname><contract_item_id>32824</contract_item_id><percent>38.5</percent></contract-item><contract-item><id>185220</id><employee_id>6523</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person2</employee_lastname><contract_item_id>32824</contract_item_id><percent>61.5</percent></contract-item></contract-commissions-items></contract-item></contract-items></contract><contract><id>17788</id><title>monthly-active-client-active-employee</title><notes /><client_id>2965</client_id><employee_id>6520</employee_id><period_id>3</period_id><active>True</active><terms>30</terms><startdate>2016-07-01-00-00-00</startdate><enddate>2016-09-11-15-53-00</enddate><invoices><invoice><id>17904</id><contract_id>17788</contract_id><date>2016-08-08-00-00-00</date><po>None</po><employerexpenserate>0.1</employerexpenserate><terms>30</terms><timecard>False</timecard><notes>None</notes><period_start>2016-08-01-00-00-00</period_start><period_end>2016-08-31-00-00-00</period_end><posted>False</posted><cleared>False</cleared><voided>False</voided><prcleared>False</prcleared><message>Thank you for your business!</message><amount>600.0</amount><created_date>2016-08-08-00-00-00</created_date><modified_date>2016-08-08-00-00-00</modified_date><created_user_id>None</created_user_id><modified_user_id>None</modified_user_id><due_date>2016-09-07-00-00-00</due_date><date_generated>2016-09-11-15-53-00</date_generated><invoice-items><invoice-item><id>32837</id><invoice_id>17904</invoice_id><description>Regular</description><amount>10.0</amount><cost>5.0</cost><quantity>12.0</quantity><cleared>False</cleared><commissions-items><invoices-items-commissions-item><id>187649</id><invoice_id>17904</invoice_id><employee_id>6522</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person1</employee_lastname><invoices_item_id>32837</invoices_item_id><description>2016-08-01-2016-08-31 Regular</description><date>2016-08-08-00-00-00</date><percent>38.5</percent><amount>20.79</amount><rel_inv_amt>None</rel_inv_amt><rel_inv_line_item_amt>None</rel_inv_line_item_amt><rel_item_amt>None</rel_item_amt><rel_item_quantity>None</rel_item_quantity><rel_item_cost>None</rel_item_cost><rel_item_amt>None</rel_item_amt><cleared>0.0</cleared><voided>None</voided><date_generated>2016-09-11-15-53-00</date_generated><created_date>2016-08-08-00-00-00</created_date><modified_date>2016-08-08-00-00-00</modified_date><created_user_id>2</created_user_id><modified_user_id>2</modified_user_id></invoices-items-commissions-item><invoices-items-commissions-item><id>187650</id><invoice_id>17904</invoice_id><employee_id>6523</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person2</employee_lastname><invoices_item_id>32837</invoices_item_id><description>2016-08-01-2016-08-31 Regular</description><date>2016-08-08-00-00-00</date><percent>61.5</percent><amount>33.21</amount><rel_inv_amt>None</rel_inv_amt><rel_inv_line_item_amt>None</rel_inv_line_item_amt><rel_item_amt>None</rel_item_amt><rel_item_quantity>None</rel_item_quantity><rel_item_cost>None</rel_item_cost><rel_item_amt>None</rel_item_amt><cleared>0.0</cleared><voided>None</voided><date_generated>2016-09-11-15-53-00</date_generated><created_date>2016-08-08-00-00-00</created_date><modified_date>2016-08-08-00-00-00</modified_date><created_user_id>2</created_user_id><modified_user_id>2</modified_user_id></invoices-items-commissions-item></commissions-items></invoice-item><invoice-item><id>32838</id><invoice_id>17904</invoice_id><description>Double Time</description><amount>20.0</amount><cost>10.0</cost><quantity>24.0</quantity><cleared>False</cleared><commissions-items><invoices-items-commissions-item><id>187651</id><invoice_id>17904</invoice_id><employee_id>6522</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person1</employee_lastname><invoices_item_id>32838</invoices_item_id><description>2016-08-01-2016-08-31 Double Time</description><date>2016-08-08-00-00-00</date><percent>38.5</percent><amount>83.16</amount><rel_inv_amt>None</rel_inv_amt><rel_inv_line_item_amt>None</rel_inv_line_item_amt><rel_item_amt>None</rel_item_amt><rel_item_quantity>None</rel_item_quantity><rel_item_cost>None</rel_item_cost><rel_item_amt>None</rel_item_amt><cleared>0.0</cleared><voided>None</voided><date_generated>2016-09-11-15-53-00</date_generated><created_date>2016-08-08-00-00-00</created_date><modified_date>2016-08-08-00-00-00</modified_date><created_user_id>2</created_user_id><modified_user_id>2</modified_user_id></invoices-items-commissions-item><invoices-items-commissions-item><id>187652</id><invoice_id>17904</invoice_id><employee_id>6523</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person2</employee_lastname><invoices_item_id>32838</invoices_item_id><description>2016-08-01-2016-08-31 Double Time</description><date>2016-08-08-00-00-00</date><percent>61.5</percent><amount>132.84</amount><rel_inv_amt>None</rel_inv_amt><rel_inv_line_item_amt>None</rel_inv_line_item_amt><rel_item_amt>None</rel_item_amt><rel_item_quantity>None</rel_item_quantity><rel_item_cost>None</rel_item_cost><rel_item_amt>None</rel_item_amt><cleared>0.0</cleared><voided>None</voided><date_generated>2016-09-11-15-53-00</date_generated><created_date>2016-08-08-00-00-00</created_date><modified_date>2016-08-08-00-00-00</modified_date><created_user_id>2</created_user_id><modified_user_id>2</modified_user_id></invoices-items-commissions-item></commissions-items></invoice-item></invoice-items><invoice-payments><invoice-payment><id>2794</id><invoice_id>17904</invoice_id><check_id>2915</check_id><amount>6.0</amount><notes>None</notes></invoice-payment></invoice-payments><employee-payments /></invoice></invoices><contract-items><contract-item><id>32825</id><active>True</active><contract_id>17788</contract_id><amt>10.0</amt><cost>5.0</cost><description>Regular</description><notes /><contract-commissions-items><contract-item><id>185221</id><employee_id>6522</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person1</employee_lastname><contract_item_id>32825</contract_item_id><percent>38.5</percent></contract-item><contract-item><id>185222</id><employee_id>6523</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person2</employee_lastname><contract_item_id>32825</contract_item_id><percent>61.5</percent></contract-item></contract-commissions-items></contract-item><contract-item><id>32826</id><active>True</active><contract_id>17788</contract_id><amt>20.0</amt><cost>10.0</cost><description>Double Time</description><notes /><contract-commissions-items><contract-item><id>185223</id><employee_id>6522</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person1</employee_lastname><contract_item_id>32826</contract_item_id><percent>38.5</percent></contract-item><contract-item><id>185224</id><employee_id>6523</employee_id><employee_firstname>sales</employee_firstname><employee_lastname>person2</employee_lastname><contract_item_id>32826</contract_item_id><percent>61.5</percent></contract-item></contract-commissions-items></contract-item></contract-items></contract></contracts><employee-commissions-items /><employee-commissions-notes><note><id>523</id><date>2016-09-11-15-53-00</date><amount>1.0</amount><notes /><employee_id>6520</employee_id><commissions_payment_id>None</commissions_payment_id><opening>None</opening><voided>None</voided><cleared>None</cleared></note></employee-commissions-notes><employee-notes-payments><notes-payment><id>523</id><employee_id>6520</employee_id><check_number /><date>2016-09-11-15-53-00</date><amount>1.0</amount><notes /><voided>None</voided></notes-payment></employee-notes-payments></employee>"""
        doc = ET.fromstring(employee_collected_base)

        assert 'firstname' == doc.findall('firstname')[0].text
        assert 1 == len(doc.findall('employee-payments/employee-payment'))
        assert 1 == len(doc.findall('memos/memo'))
        assert 4 == len(doc.findall('contracts/contract'))
        assert 4 == len(doc.findall('contracts/contract/invoices/invoice'))
        assert 8 == len(doc.findall('contracts/contract/contract-items/contract-item'))
        assert 8 == len(doc.findall('contracts/contract/invoices/invoice/invoice-items/invoice-item'))
        assert 8 == len(doc.findall('contracts/contract/invoices/invoice/invoice-items/invoice-item/commissions-items'))
        assert 16 == len(doc.findall('contracts/contract/invoices/invoice/invoice-items/invoice-item/commissions-items/invoices-items-commissions-item'))
        base_emp_doc = doc
        doc = employee_attach_collected_contracts(original_saved_emp, [i for i in base_emp_doc.findall('contracts/contract')])

        assert 'firstname' == doc.findall('firstname')[0].text
        assert 1 == len(doc.findall('employee-payments/employee-payment'))
        assert 1 == len(doc.findall('memos/memo'))
        assert 4 == len(doc.findall('contracts/contract'))
        assert 4 == len(doc.findall('contracts/contract/invoices/invoice'))
        assert 8 == len(doc.findall('contracts/contract/contract-items/contract-item'))
        assert 8 == len(doc.findall('contracts/contract/invoices/invoice/invoice-items/invoice-item'))
        assert 8 == len(doc.findall('contracts/contract/invoices/invoice/invoice-items/invoice-item/commissions-items'))
        assert 16 == len(doc.findall('contracts/contract/invoices/invoice/invoice-items/invoice-item/commissions-items/invoices-items-commissions-item'))

