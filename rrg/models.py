"""
does not work on alpine because libmysqlclient-dev package is not available.
"""
import os
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
from sqlalchemy import create_engine
from sqlalchemy import TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
import xml.etree.ElementTree as ET

from s3_mysql_backup import TIMESTAMP_FORMAT

from rrg.helpers import date_to_datetime
from rrg.helpers import MissingEnvVar

try:
    env_str = 'DB_USER'
    if os.getenv(env_str) is None:
       raise MissingEnvVar('%s is not set' % env_str)
    else:
       DB_USER = os.getenv(env_str)

    env_str = 'DB_PASS'
    if os.getenv(env_str) is None:
       raise MissingEnvVar('%s is not set' % env_str)
    else:
       DB_PASS = os.getenv(env_str)

    env_str = 'MYSQL_SERVER_PORT_3306_TCP_ADDR'
    if os.getenv(env_str) is None:
       raise MissingEnvVar('%s is not set' % env_str)
    else:
       MYSQL_PORT_3306_TCP_ADDR = os.getenv(env_str)

    env_str = 'MYSQL_SERVER_PORT_3306_TCP_PORT'
    if os.getenv(env_str) is None:
       raise MissingEnvVar('%s is not set' % env_str)
    else:
       MYSQL_PORT_3306_TCP_PORT = os.getenv(env_str)

except MissingEnvVar as e:
    print(e.value)
    raise


engine = create_engine(
             'mysql+mysqldb://%s:%s@%s:%s/rrg' % (
             DB_USER, DB_PASS, MYSQL_PORT_3306_TCP_ADDR, MYSQL_PORT_3306_TCP_PORT))


Base = declarative_base()

# Models for Commissions, Invoices, and Invoice Items are in sherees_commissions


class Employee(Base):

    __tablename__ = 'employees'

    id = Column(Integer, primary_key=True)
    firstname = Column(String)
    lastname = Column(String)
    dob = Column(Date)
    salesforce = Column(Boolean)
    comm_items = relationship("Citem", back_populates="employee")

class Note(Base):
    __tablename__ = 'notes'

    id = Column(Integer, primary_key=True)

    employee_id = Column(Integer, ForeignKey('employees.id'))
    employee = relationship("Employee")
    commissions_payment_id = Column(Integer, ForeignKey('commissions_payments.id'))
    commissions_payment = relationship("CommPayment")
    date = Column(Date, index=True)
    amount = Column(Float)
    notes = Column(String)
    opening = Column(Boolean)
    voided = Column(Boolean)
    cleared = Column(Boolean)
    created_date = Column(Date)
    modified_date = Column(Date)
    modified_user = Column(Integer)
    created_user = Column(Integer)

class CommPayment(Base):
    __tablename__ = 'commissions_payments'

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey('employees.id'))
    employee = relationship("Employee")
    date = Column(Date, index=True)
    amount = Column(Float)
    description = Column(String)
    check_number = Column(String)
    cleared = Column(Boolean)
    voided = Column(Boolean)

class Client(Base):

    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    street1 = Column(String)
    street2 = Column(String)
    city = Column(String)
    state_id = Column(Integer)
    zip = Column(String)
    active = Column(Boolean)
    terms = Column(Integer)
    hq = Column(Boolean)
    modified_date = Column(Date)
    created_date = Column(Date)
    modified_user = Column(Integer)
    created_user = Column(Integer)
    last_sync_time = Column(Date)


class Contract(Base):

    __tablename__ = 'clients_contracts'

    id = Column(Integer, primary_key=True)

    client_id = Column(Integer, ForeignKey('clients.id'))
    client = relationship("Client")

    employee_id = Column(Integer, ForeignKey('employees.id'))
    employee = relationship("Employee")

    notes = Column(String)
    title = Column(String)
    startdate = Column(Date)
    enddate = Column(Date)


class Invoice(Base):

    __tablename__ = 'invoices'

    id = Column(Integer, primary_key=True)

    contract_id = Column(Integer, ForeignKey('clients_contracts.id'))
    contract = relationship("Contract", backref="clients_contracts")

    invoice_items = relationship("Iitem", back_populates="invoice")

    date = Column(Date, index=True)
    po = Column(String)
    employerexpenserate = Column(Float)
    terms = Column(Integer)
    timecard = Column(Boolean)
    notes = Column(String)
    period_start = Column(Date)
    period_end = Column(Date)

    posted = Column(Boolean)
    cleared = Column(Boolean)
    cleared_date = Column(Date)
    prcleared = Column(Boolean)
    timecard_receipt_sent = Column(Boolean)
    message = Column(TEXT)

    amount = Column(Float)
    voided = Column(Boolean)

    token = Column(String)
    view_count = Column(Integer)
    mock = Column(Boolean)
    timecard_document = Column(TEXT)
    created_date = Column(Date)
    modified_date = Column(Date)
    created_user_id = Column(Integer)
    modified_user_id = Column(Integer)
    last_sync_time = Column(TIMESTAMP)

    def __repr__(self):
        return "<Invoice(contract.title='%s', amount='%s', duedate='%s')>" % (
            self.contract.title, self.amount, self.duedate())

    def duedate(self):
        if self.date:
            return date_to_datetime(self.date) + td(days=self.terms)
        else:
            return None

    def is_pastdue(self):
        """
        returns true or false if invoice is pastdue, server day

        :return:
        """

        if self.duedate() >= dt.now():
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
    post_ab = Column(String)
    capital = Column(String)
    date = Column(String)
    flower = Column(String)
    name = Column(String)
    state_no = Column(String)


class User(Base):

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    firstname = Column(String)
    lastname = Column(String)


class Iitem(Base):

    __tablename__ = 'invoices_items'

    id = Column(Integer, primary_key=True)

    invoice_id = Column(Integer, ForeignKey('invoices.id'))
    invoice = relationship("Invoice", back_populates='invoice_items')

    description = Column(String)
    amount = Column(Float)
    quantity = Column(Float)
    cost = Column(Float)
    ordering = Column(Integer)
    cleared = Column(Boolean)
    comm_items = relationship("Citem", back_populates="invoices_item")


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
    description = Column(String)
    date = Column(Date, index=True)
    percent = Column(Float)
    amount = Column(Float)
    rel_inv_amt = Column(Float)
    rel_inv_line_item_amt = Column(Float)
    rel_item_amt = Column(Float)
    rel_item_quantity = Column(Float)
    rel_item_cost = Column(Float)
    cleared = Column(Float)
    voided = Column(Float)
    created_date = Column(Date)
    modified_date = Column(Date)
    created_user_id = Column(Integer)
    modified_user_id = Column(Integer)
    last_sync_time = Column(TIMESTAMP)

    def __repr__(self):

        print(type(self.modified_date))
        return "<Citem(description='%s', id='%s', employee_id='%s', amount='%s'. mod_date='%s'. last_sync='%s')>" % (
            self.description, self.id, self.employee_id, self.amount, self.modified_date,
            self.last_sync_time.strftime(TIMESTAMP_FORMAT))

    def to_xml(self):
        doc = ET.Element('invoices-items-commissions-item')

        id = ET.SubElement(doc, 'id')
        id.text = str(self.id)

        invoice_id = ET.SubElement(doc, 'invoice_id')
        invoice_id.text = str(self.invoices_item.invoice_id)

        employee_id = ET.SubElement(doc, 'employee_id')
        employee_id.text = str(self.employee_id)

        invoices_item_id = ET.SubElement(doc, 'invoices_item_id')
        invoices_item_id.text = str(self.invoices_item_id)

        commissions_report_id = ET.SubElement(doc, 'commissions_report_id')
        commissions_report_id.text = str(self.commissions_report_id)

        commissions_reports_tag_id = ET.SubElement(doc, 'commissions_reports_tag_id')
        commissions_reports_tag_id.text = str(self.commissions_reports_tag_id)

        description = ET.SubElement(doc, 'description')
        description.text = self.description

        date = ET.SubElement(doc, 'date')
        date.text = dt.strftime(self.date, TIMESTAMP_FORMAT)

        percent = ET.SubElement(doc, 'percent')
        percent.text = str(self.percent)

        amount = ET.SubElement(doc, 'amount')
        amount.text = str(self.amount)

        rel_inv_amt = ET.SubElement(doc, 'rel_inv_amt')
        rel_inv_amt.text = str(self.rel_inv_amt)

        rel_inv_line_item_amt = ET.SubElement(doc, 'rel_inv_line_item_amt')
        rel_inv_line_item_amt.text = str(self.rel_inv_line_item_amt)

        rel_item_amt = ET.SubElement(doc, 'rel_item_amt')
        rel_item_amt.text = str(self.rel_item_amt)

        rel_item_quantity = ET.SubElement(doc, 'rel_item_quantity')
        rel_item_quantity.text = str(self.rel_item_quantity)

        rel_item_cost = ET.SubElement(doc, 'rel_item_cost')
        rel_item_cost.text = str(self.rel_item_cost)

        rel_item_cost = ET.SubElement(doc, 'rel_item_amt')
        rel_item_cost.text = str(self.rel_item_amt)

        cleared = ET.SubElement(doc, 'cleared')
        cleared.text = str(self.cleared)

        voided = ET.SubElement(doc, 'voided')
        voided.text = str(self.voided)

        date_generated = ET.SubElement(doc, 'date_generated')
        date_generated.text = dt.strftime(dt.now(), TIMESTAMP_FORMAT)

        return doc

    @staticmethod
    def from_xml(xml_file_name):
        """
        returns DOM of comm item from file
        """
        return ET.parse(xml_file_name).getroot()

