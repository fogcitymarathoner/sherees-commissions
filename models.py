"""
does not work on alpine because libmysqlclient-dev package is not available.
"""
import os
from datetime import datetime as dt
from sqlalchemy import create_engine
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Date
from sqlalchemy import Float
from sqlalchemy import Boolean
from sqlalchemy import TIMESTAMP
from sqlalchemy import TEXT
from sqlalchemy import ForeignKey

from sqlalchemy.orm import relationship

from sqlalchemy.ext.declarative import declarative_base
import xml.etree.ElementTree as ET

from s3_mysql_backup import TIMESTAMP_FORMAT


class MissingEnvVar(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

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

    env_str = 'MYSQL_PORT_3306_TCP_ADDR'
    if os.getenv(env_str) is None:
       raise MissingEnvVar('%s is not set' % env_str)
    else:
       MYSQL_PORT_3306_TCP_ADDR = os.getenv(env_str)

    env_str = 'MYSQL_PORT_3306_TCP_PORT'
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


class Invoice(Base):

    __tablename__ = 'invoices'

    id = Column(Integer, primary_key=True)
    contract_id = Column(Integer)
    date = Column(Date)
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


class Iitem(Base):

    __tablename__ = 'invoices_items'

    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer)
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
    employee_id = Column(Integer)
    invoices_item_id = Column(Integer, ForeignKey('invoices_items.id'))
    invoices_item = relationship("Iitem", back_populates="comm_items")
    commissions_report_id = Column(Integer)
    commissions_reports_tag_id = Column(Integer)
    description = Column(String)
    date = Column(Date)
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
       return "<Citem(description='%s', id='%s', employee_id='%s', amount='%s')>" % (
           self.description, self.id, self.employee_id, self.amount)

    def to_xml(self):
        doc = ET.Element('invoices-items-commissions-item')

        id = ET.SubElement(doc, 'id')
        id.text = str(self.id)

        invoice_id = ET.SubElement(doc, 'invoice_id')
        invoice_id.text = str(self.invoice_item.invoice_id)

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

        return ET.dump(doc)
