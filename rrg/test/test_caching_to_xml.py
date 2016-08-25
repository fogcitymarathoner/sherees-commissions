import sys
from datetime import datetime as dt
from datetime import timedelta as td
import logging
import xml.etree.ElementTree as ET
from freezegun import freeze_time

from rrg import MYSQL_PORT_3306_TCP_ADDR
from rrg.models import Contract
from rrg.models import ContractItem
from rrg.models import ContractItemCommItem
from rrg.models import Client
from rrg.models import Employee
from rrg.models import Invoice
from rrg.models import Iitem
from rrg.models import Citem
from rrg.models import periods
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

            objects = []

            employee_active = Employee(firstname='firstname',
                                       lastname='activelastname', active=True)
            employee_inactive = Employee(firstname='firstname',
                                         lastname='inactivelastname',
                                         active=False)
            employee_sales_person1 = Employee(firstname='sales',
                                              lastname='person1', active=True)
            employee_sales_person2 = Employee(firstname='sales',
                                              lastname='person2', active=True)

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
        assert 'localhost' == MYSQL_PORT_3306_TCP_ADDR

    def test_inv_to_xml(self):
        """
        test xml output of invoice
        :return:
        """
        baseline_string = """<invoice><id>26</id><contract_id>25</contract_id><date>2016-08-08-00-00-00</date><po>None</po><employerexpenserate>None</employerexpenserate><terms>30</terms><timecard>None</timecard><notes>None</notes><period_start>2016-07-11-00-00-00</period_start><period_end>2016-07-17-00-00-00</period_end><posted>None</posted><cleared>None</cleared><voided>None</voided><prcleared>None</prcleared><message>None</message><amount>None</amount><created_date>2016-08-07-00-00-00</created_date><modified_date>2016-08-07-00-00-00</modified_date><created_user_id>None</created_user_id><modified_user_id>None</modified_user_id><due_date>2016-09-07-00-00-00</due_date></invoice>"""
        base_doc = ET.fromstring(baseline_string)
        inv = self.session.query(Invoice)[0]

        ele = inv.to_xml()
        assert base_doc.findall('period_start')[0].text == \
               ele.findall('period_start')[0].text
        assert base_doc.findall('period_end')[0].text == \
               ele.findall('period_end')[0].text

    def test_citem_to_xml(self):
        """
        test xml output of commissions item
        :return:
        """
        baseline_string = """<invoices-items-commissions-item><id>8541</id><employee_id>1660</employee_id><invoices_item_id>None</invoices_item_id><commissions_report_id>None</commissions_report_id><commissions_reports_tag_id>None</commissions_reports_tag_id><date>2016-08-21-00-00-00</date><percent>38.5</percent><amount>None</amount><rel_inv_amt>None</rel_inv_amt><rel_inv_line_item_amt>None</rel_inv_line_item_amt><rel_item_amt>None</rel_item_amt><rel_item_quantity>None</rel_item_quantity><rel_item_cost>None</rel_item_cost><rel_item_amt>None</rel_item_amt><cleared>None</cleared><voided>None</voided><date_generated>2016-08-21-09-48-50</date_generated><created_date>2016-08-21-00-00-00</created_date><modified_date>2016-08-21-00-00-00</modified_date><created_user_id>2</created_user_id><modified_user_id>2</modified_user_id></invoices-items-commissions-item>"""
        base_doc = ET.fromstring(baseline_string)
        citem = self.session.query(Citem)[0]

        ele = citem.to_xml()
        logger.debug('test_citem_to_xml citem')
        logger.debug(citem)
        logger.debug('test_citem_to_xml citem.to_xml()')
        logger.debug(ET.tostring(citem.to_xml()))
        # fixme: add assertions against contract/invoice particulars
        1 == len(ele.findall('invoices-items-commissions-item'))

    def test_iitem_to_xml(self):
        """
        test xml output of invoice item
        :return:
        """
        baseline_string = """<invoice-item><id>1126</id><invoice_id>None</invoice_id><description>Regular</description><amount>10.0</amount><quantity>None</quantity><cleared>None</cleared></invoice-item>"""
        base_doc = ET.fromstring(baseline_string)
        iitem = self.session.query(Iitem)[0]
        logger.debug('iitem')
        logger.debug(iitem)
        ele = iitem.to_xml()
        logger.debug('iitem-ele')
        logger.debug(ET.tostring(iitem.to_xml()))
        assert base_doc.findall('amount')[0].text == ele.findall('amount')[
            0].text
        logger.debug('base_doc.findall("quantity")[0].text')
        logger.debug(base_doc.findall('quantity')[0].text)
        logger.debug('ele.findall("quantity")[0]')
        logger.debug(ele.findall('quantity')[0])
        logger.debug('count')
        logger.debug(len(ele.findall('quantity')))
        logger.debug('ele.findall("quantity")[0].text')
        logger.debug(ele.findall('quantity')[0].text)
        assert base_doc.findall('quantity')[0].text == ele.findall('quantity')[
            0].text
