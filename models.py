"""
does not work on alpine because libmysqlclient-dev package is not available.
"""
import os 
import sqlalchemy

from sqlalchemy import create_engine
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Date
from sqlalchemy import Float
from sqlalchemy import Boolean
from sqlalchemy import TIMESTAMP
from sqlalchemy import TEXT
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


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

Session = sessionmaker(bind=engine)

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

class Citem(Base):

    __tablename__ = 'invoices_items_commissions_items'
    
    id = Column(Integer, primary_key=True)
    invoices_item_id = Column(Integer)
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
       return "<User(name='%s', fullname='%s', password='%s')>" % (self.name, self.fullname, self.password)

session = Session()
for instance in session.query(Invoice).order_by(Invoice.id):
    print(instance.amount)

