"""
does not work on alpine because libmysqlclient-dev package is not available.
"""

from datetime import date
from datetime import datetime as dt
from datetime import timedelta as td

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Date
from sqlalchemy import Boolean
from sqlalchemy import ForeignKey
from sqlalchemy import TEXT
from sqlalchemy import Float
from sqlalchemy.orm import relationship
from sqlalchemy import TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
import xml.etree.ElementTree as ET

from s3_mysql_backup import TIMESTAMP_FORMAT

from rrg.helpers import date_to_datetime

from sqlalchemy.orm import sessionmaker

from sqlalchemy import create_engine

def default_date():
    return date.today()

def session_maker(args):
    engine = create_engine(
        'mysql+mysqldb://%s:%s@%s:%s/%s' % (
        args.db_user, args.db_pass, args.mysql_host, args.mysql_port, args.db))

    session = sessionmaker(bind=engine)
    return session()


periods = {
    'week': 1,
    'semimonth': 2,
    'month': 3,
    'biweek': 5,
}

Base = declarative_base()


# Models for Commissions, Invoices, and Invoice Items are in
# sherees_commissions


class Employee(Base):
    __tablename__ = 'employees'

    id = Column(Integer, primary_key=True)

    active = Column(Boolean)

    firstname = Column(String(20))
    lastname = Column(String(20))
    dob = Column(Date)
    salesforce = Column(Boolean)
    comm_items = relationship("Citem", back_populates="employee")
    notes = relationship("Note", back_populates="employee")
    notes_payments = relationship("NotePayment", back_populates="employee")
    contracts = relationship("Contract", back_populates="employee")

    voided = Column(Boolean)

    def __repr__(self):
        return "<Employee(id='%s', firstname='%s', lastname='%s')>" % (
            self.id, self.firstname, self.lastname)


class NotePayment(Base):
    __tablename__ = 'notes_payments'

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey('employees.id'))
    employee = relationship("Employee")
    check_number = Column(String(25))
    date = Column(Date, index=True)
    amount = Column(Float)
    notes = Column(String(100))
    voided = Column(Boolean)
    created_date = Column(Date, default=default_date)
    modified_date = Column(Date, default=default_date, onupdate=default_date)
    modified_user_id = Column(Integer)
    created_user_id = Column(Integer)

    def __repr__(self):
        return "<NotePayment(id='%s', employee='%s %s', check_number='%s', date='%s', amount='%s', notes='%s')>" % (
            self.id, self.employee.firstname, self.employee.lastname,
            self.check_number, self.date, self.amount,
            self.notes)


class Note(Base):
    __tablename__ = 'notes'

    id = Column(Integer, primary_key=True)

    employee_id = Column(Integer, ForeignKey('employees.id'))
    employee = relationship("Employee")

    commissions_payment_id = Column(
        Integer, ForeignKey('commissions_payments.id'))
    commissions_payment = relationship("CommPayment")

    date = Column(Date, index=True)
    amount = Column(Float)
    notes = Column(String(100))
    opening = Column(Boolean)
    voided = Column(Boolean)
    cleared = Column(Boolean)
    created_date = Column(Date, default=default_date)
    modified_date = Column(Date, default=default_date, onupdate=default_date)
    modified_user_id = Column(Integer)
    created_user_id = Column(Integer)


class CommPayment(Base):
    __tablename__ = 'commissions_payments'

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey('employees.id'))
    employee = relationship("Employee")
    date = Column(Date, index=True)
    amount = Column(Float)
    description = Column(TEXT)
    check_number = Column(String(10))
    cleared = Column(Boolean)
    voided = Column(Boolean)

    def __repr__(self):
        return "<CommissionsPayment(id='%s', employee='%s %s', check_number='%s', date='%s', amount='%s'," \
               " description='%s')>" % (
                   self.id, self.employee.firstname, self.employee.lastname,
                   self.check_number, self.date, self.amount,
                   self.description)


class Client(Base):
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    street1 = Column(String(50))
    street2 = Column(String(50))
    city = Column(String(50))
    state_id = Column(Integer)
    zip = Column(String(50))
    active = Column(Boolean)
    terms = Column(Integer, nullable=False)
    hq = Column(Boolean)
    modified_date = Column(Date)
    created_date = Column(Date, default=default_date)
    modified_date = Column(Date, default=default_date, onupdate=default_date)
    created_user = Column(Integer)
    last_sync_time = Column(Date)

    def __repr__(self):
        return "<Client(id='%s', name='%s')>" % (self.id, self.name)


class ContractItemCommItem(Base):
    __tablename__ = 'contracts_items_commissions_items'

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    employee = relationship("Employee")

    contract_item_id = Column(Integer, ForeignKey('contracts_items.id'),
                              nullable=False)
    contract_item = relationship("ContractItem")
    percent = Column(Float)
    modified_date = Column(Date)
    created_date = Column(Date, default=default_date)
    modified_date = Column(Date, default=default_date, onupdate=default_date)
    created_user_id = Column(Integer)


class ContractItem(Base):
    __tablename__ = 'contracts_items'

    id = Column(Integer, primary_key=True)
    active = Column(Boolean)

    contract_id = Column(Integer, ForeignKey('clients_contracts.id'),
                         nullable=False)
    contract = relationship("Contract")

    contract_comm_items = relationship("ContractItemCommItem",
                                       back_populates="contract_item")

    amt = Column(Float)
    cost = Column(Float)
    description = Column(TEXT)

    notes = Column(TEXT)
    created_date = Column(Date, default=default_date)
    modified_date = Column(Date, default=default_date, onupdate=default_date)
    modified_user_id = Column(Integer)
    created_user_id = Column(Integer)
    last_sync_time = Column(Date)

    def __repr__(self):
        return "<ContractItem(id='%s', description='%s')>" % (
        self.id, self.description)


class Contract(Base):
    __tablename__ = 'clients_contracts'

    id = Column(Integer, primary_key=True)

    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    client = relationship("Client")
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    employee = relationship("Employee")

    contract_items = relationship("ContractItem", back_populates="contract")
    period_id = Column(Integer)
    active = Column(Boolean)
    notes = Column(TEXT)
    title = Column(TEXT)
    terms = Column(Integer, nullable=False)
    startdate = Column(Date)
    enddate = Column(Date)

    def __repr__(self):
        return "<Contract(id='%s', client=%s, title='%s', employee='%s %s')>" % (
            self.id, self.client.name, self.title, self.employee.firstname,
            self.employee.lastname)


class Invoice(Base):
    __tablename__ = 'invoices'

    id = Column(Integer, primary_key=True)

    contract_id = Column(Integer, ForeignKey('clients_contracts.id'),
                         nullable=False)

    contract = relationship("Contract", backref="clients_contracts")

    invoice_items = relationship("Iitem", back_populates="invoice")

    date = Column(Date, nullable=False)

    po = Column(String(30))
    employerexpenserate = Column(Float)
    terms = Column(Integer, nullable=False)
    timecard = Column(Boolean)
    notes = Column(String(160))
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)

    posted = Column(Boolean)
    cleared = Column(Boolean)
    cleared_date = Column(Date)
    prcleared = Column(Boolean)
    timecard_receipt_sent = Column(Boolean)
    message = Column(TEXT)

    amount = Column(Float)
    voided = Column(Boolean)

    token = Column(String(64))
    view_count = Column(Integer)
    mock = Column(Boolean)
    timecard_document = Column(TEXT)
    created_date = Column(Date, default=default_date)
    modified_date = Column(Date, default=default_date, onupdate=default_date)
    created_user_id = Column(Integer)
    modified_user_id = Column(Integer)
    last_sync_time = Column(TIMESTAMP)

    def __repr__(self):
        return "<Invoice(id='%s', contract_id='%s', amount='%s', " \
               "duedate='%s', period_start='%s', " \
               "period_end='%s', date='%s')>" % (
                   self.id, self.contract_id, self.amount, self.duedate(),
                   self.period_start, self.period_end, self.date)

    def duedate(self):
        return date_to_datetime(self.date) + td(days=self.terms)

    def to_xml(self):
        doc = ET.Element('invoice')

        ET.SubElement(doc, 'id').text = str(self.id)
        ET.SubElement(doc, 'contract_id').text = str(self.contract_id)
        ET.SubElement(doc, 'date').text = dt.strftime(self.date,
                                                      TIMESTAMP_FORMAT)
        ET.SubElement(doc, 'po').text = str(self.po)
        ET.SubElement(doc, 'employerexpenserate').text = str(
            self.employerexpenserate)
        ET.SubElement(doc, 'terms').text = str(self.terms)
        ET.SubElement(doc, 'timecard').text = str(self.timecard)
        ET.SubElement(doc, 'notes').text = str(self.notes)
        ET.SubElement(doc, 'period_start').text = dt.strftime(
            self.period_start, TIMESTAMP_FORMAT)
        ET.SubElement(doc, 'period_end').text = dt.strftime(self.period_end,
                                                            TIMESTAMP_FORMAT)
        ET.SubElement(doc, 'posted').text = str(self.posted)
        ET.SubElement(doc, 'cleared').text = str(self.cleared)
        ET.SubElement(doc, 'voided').text = str(self.voided)
        ET.SubElement(doc, 'prcleared').text = str(self.prcleared)
        ET.SubElement(doc, 'message').text = str(self.message)
        ET.SubElement(doc, 'amount').text = str(self.amount)
        ET.SubElement(doc, 'created_date').text = dt.strftime(
            self.created_date, TIMESTAMP_FORMAT)
        ET.SubElement(doc, 'modified_date').text = dt.strftime(
            self.modified_date, TIMESTAMP_FORMAT)
        ET.SubElement(doc, 'created_user_id').text = str(self.created_user_id)
        ET.SubElement(doc, 'modified_user_id').text = str(
            self.modified_user_id)
        ET.SubElement(doc, 'due_date').text = dt.strftime(self.duedate(),
                                                          TIMESTAMP_FORMAT)
        ET.SubElement(doc, 'date_generated').text = dt.strftime(dt.now(),
                                                                TIMESTAMP_FORMAT)
        return doc


def is_pastdue(inv, date=None):
    """
    returns true or false if invoice is pastdue, server day

    :return:
    """
    if not date:
        date = dt.now()
    if inv.duedate() >= date:
        return True
    else:
        return False


# XML


def invoice_archives(root, invoice_state='pastdue'):
    """
    returns xml invoice id list for invoice states 'pastdue', 'open', 'cleared' and 'all'
    """
    res = []
    for i in root.findall('./%s/invoice' % invoice_state):
        res.append(i.text)
    return res


class State(Base):
    __tablename__ = 'states'

    id = Column(Integer, primary_key=True)
    post_ab = Column(String(2))
    capital = Column(String(14))
    date = Column(String(10))
    flower = Column(String(27))
    name = Column(String(14))
    state_no = Column(String(9))


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    firstname = Column(String(60))

    lastname = Column(String(60))


class Iitem(Base):
    """

    """
    __tablename__ = 'invoices_items'

    id = Column(Integer, primary_key=True)

    invoice_id = Column(Integer, ForeignKey('invoices.id'), nullable=False)
    invoice = relationship("Invoice", back_populates='invoice_items')

    description = Column(String(60))
    amount = Column(Float)
    quantity = Column(Float)
    cost = Column(Float)
    ordering = Column(Integer)
    cleared = Column(Boolean)
    comm_items = relationship("Citem", back_populates="invoices_item")
    last_sync_time = Column(TIMESTAMP)

    def __repr__(self):
        return "<InvoiceItem(id='%s', description='%s', amount='%s', quantity='%s', invoice.id='%s')>" % (
                   self.id, self.description, self.amount, self.quantity, self.invoice_id)

    def to_xml(self):
        doc = ET.Element('invoice-item')

        ET.SubElement(doc, 'id').text = str(self.id)
        ET.SubElement(doc, 'invoice_id').text = str(self.invoice_id)
        ET.SubElement(doc, 'description').text = str(self.description)
        ET.SubElement(doc, 'amount').text = str(self.amount)
        ET.SubElement(doc, 'quantity').text = str(self.quantity)
        ET.SubElement(doc, 'cleared').text = str(self.cleared)

        return doc


class Citem(Base):
    """
    commissions item
    """

    __tablename__ = 'invoices_items_commissions_items'

    id = Column(Integer, primary_key=True)

    employee_id = Column(Integer, ForeignKey('employees.id'))
    employee = relationship("Employee", back_populates="comm_items")

    invoices_item_id = Column(Integer, ForeignKey('invoices_items.id'))
    invoices_item = relationship("Iitem", back_populates="comm_items")

    commissions_report_id = Column(Integer)
    commissions_reports_tag_id = Column(Integer)
    description = Column(String(50))
    date = Column(Date, index=True, default=default_date)
    percent = Column(Float)
    amount = Column(Float)
    rel_inv_amt = Column(Float)
    rel_inv_line_item_amt = Column(Float)
    rel_item_amt = Column(Float)
    rel_item_quantity = Column(Float)
    rel_item_cost = Column(Float)
    cleared = Column(Float)
    voided = Column(Float)
    created_date = Column(Date, default=default_date)
    modified_date = Column(Date, default=default_date, onupdate=default_date)
    created_user_id = Column(Integer, default=2)
    modified_user_id = Column(Integer, default=2)
    last_sync_time = Column(TIMESTAMP)

    def __repr__(self):
        return "<Citem(description='%s', id='%s', employee_id='%s', amount='%s'. mod_date='%s')>" % (
            self.description, self.id, self.employee_id, self.amount,
            self.modified_date)

    def to_xml(self):
        doc = ET.Element('invoices-items-commissions-item')

        ET.SubElement(doc, 'id').text = str(self.id)
        # fixme: put back after next data migration
        # ET.SubElement(doc, 'invoice_id').text = str(self.invoices_item.invoice_id)
        ET.SubElement(doc, 'employee_id').text = str(self.employee_id)
        ET.SubElement(doc, 'invoices_item_id').text = str(
            self.invoices_item_id)
        ET.SubElement(doc, 'commissions_report_id').text = str(
            self.commissions_report_id)
        ET.SubElement(
            doc, 'commissions_reports_tag_id').text = str(
            self.commissions_reports_tag_id)
        # ET.SubElement(doc, 'description').text = '%s-%s %s' % (
        #     dt.strftime(self.invoices_item.invoice.period_start, YMD_FORMAT),
        #     dt.strftime(self.invoices_item.invoice.period_end, YMD_FORMAT),
        #     self.description)
        ET.SubElement(doc, 'date').text = dt.strftime(self.date,
                                                      TIMESTAMP_FORMAT)
        ET.SubElement(doc, 'percent').text = str(self.percent)
        ET.SubElement(doc, 'amount').text = str(self.amount)
        ET.SubElement(doc, 'rel_inv_amt').text = str(self.rel_inv_amt)
        ET.SubElement(doc, 'rel_inv_line_item_amt').text = str(
            self.rel_inv_line_item_amt)
        ET.SubElement(doc, 'rel_item_amt').text = str(self.rel_item_amt)
        ET.SubElement(doc, 'rel_item_quantity').text = str(
            self.rel_item_quantity)
        ET.SubElement(doc, 'rel_item_cost').text = str(self.rel_item_cost)
        ET.SubElement(doc, 'rel_item_amt').text = str(self.rel_item_amt)
        ET.SubElement(doc, 'cleared').text = str(self.cleared)
        ET.SubElement(doc, 'voided').text = str(self.voided)
        ET.SubElement(doc, 'date_generated').text = dt.strftime(dt.now(),
                                                                TIMESTAMP_FORMAT)

        ET.SubElement(doc, 'created_date').text = dt.strftime(
            self.created_date, TIMESTAMP_FORMAT)
        ET.SubElement(doc, 'modified_date').text = dt.strftime(
            self.modified_date, TIMESTAMP_FORMAT)
        ET.SubElement(doc, 'created_user_id').text = str(self.created_user_id)
        ET.SubElement(doc, 'modified_user_id').text = str(
            self.modified_user_id)
        return doc

    @staticmethod
    def from_xml(xml_file_name):
        """
        returns DOM of comm item from file
        """
        return ET.parse(xml_file_name).getroot()
