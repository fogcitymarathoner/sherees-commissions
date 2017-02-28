"""
does not work on alpine because libmysqlclient-dev package is not available.
"""
import re
from datetime import date
from datetime import datetime as dt
from datetime import timedelta as td

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Date
from sqlalchemy import DateTime
from sqlalchemy import Boolean
from sqlalchemy import ForeignKey
from sqlalchemy import TEXT
from sqlalchemy import Float
from sqlalchemy.orm import relationship
from sqlalchemy import TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

import xml.etree.ElementTree as ET

from s3_mysql_backup import TIMESTAMP_FORMAT
from s3_mysql_backup import YMD_FORMAT

from rrg.helpers import date_to_datetime


def default_date():
    return date.today()


def session_maker(db_user, db_pass, mysql_host, mysql_port, db):
    engine = create_engine(
        'mysql+mysqldb://%s:%s@%s:%s/%s' % (db_user, db_pass, mysql_host, mysql_port, db))

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


def commissions_calculation(inv_item_quantity, inv_item_amount, inv_item_cost, employerexpenserate, percent):
    iamount = inv_item_quantity * inv_item_amount
    icost = inv_item_quantity * inv_item_cost
    empexp = employerexpenserate * icost
    presplit_comm = iamount - icost - empexp
    return presplit_comm * percent / 100


class EmployeePayment(Base):
    __tablename__ = 'employees_payments'
    id = Column(Integer, primary_key=True)

    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    employee = relationship("Employee")

    invoice_id = Column(Integer, ForeignKey('invoices.id'), nullable=False)
    invoice = relationship("Invoice")

    payroll_id = Column(Integer, ForeignKey('payrolls.id'), nullable=False)
    payroll = relationship("Payroll")

    notes = Column(String(100))
    ref = Column(String(20))
    amount = Column(Float)
    date = Column(Date, nullable=False)
    created_date = Column(Date, default=default_date)
    modified_date = Column(DateTime, default=func.now(), onupdate=func.now())
    created_user_id = Column(Integer)
    modified_user_id = Column(Integer)
    last_sync_time = Column(TIMESTAMP)

    def __repr__(self):
        return "<EmployeePayment(id='%s', firstname='%s', lastname='%s', invoice_id='%s', " \
               "start='%s', end='%s', date='%s', amount='%s')>" % (
                   self.id, self.employee.firstname, self.employee.lastname, self.invoice_id, self.invoice.period_start,
                   self.invoice.period_end, self.date, self.amount)

    def to_xml(self, crypter):
        doc = ET.Element('employee-payment')
        ET.SubElement(doc, 'id').text = str(self.id)
        eattributes = {'fullname': '%s %s' % (self.employee.firstname, self.employee.lastname)}
        ET.SubElement(doc, 'employee_id', attrib=eattributes).text = str(self.employee_id)
        ET.SubElement(doc, 'invoice_id').text = str(self.invoice_id)
        ET.SubElement(doc, 'payroll_id').text = str(self.payroll_id)
        ET.SubElement(doc, 'notes').text = self.notes
        ET.SubElement(doc, 'ref').text = self.ref
        ET.SubElement(doc, 'date').text = dt.strftime(self.date, TIMESTAMP_FORMAT)
        ET.SubElement(doc, 'amount').text = str(self.amount)
        return doc


class EmployeeMemo(Base):
    __tablename__ = 'employees_memos'

    id = Column(Integer, primary_key=True)

    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    employee = relationship("Employee")

    notes = Column(String(100))
    date = Column(Date, nullable=False)
    created_date = Column(Date, default=default_date)
    modified_date = Column(DateTime, default=func.now(), onupdate=func.now())
    created_user_id = Column(Integer)
    modified_user_id = Column(Integer)
    last_sync_time = Column(TIMESTAMP)

    def __repr__(self):
        return "<EmployeeMemo(id='%s', employee='%s %s', date='%s', notes='%s')>" % (
            self.id, self.employee.firstname, self.employee.lastname, dt.strftime(self.date, TIMESTAMP_FORMAT),
            self.notes)

    def to_xml(self, crypter):
        doc = ET.Element('memo')
        ET.SubElement(doc, 'id').text = str(self.id)
        ET.SubElement(doc, 'employee_id').text = str(self.employee_id)
        ET.SubElement(doc, 'notes').text = re.sub(r'[^\x00-\x7F]', ' ', self.notes)
        ET.SubElement(doc, 'date').text = dt.strftime(self.date, TIMESTAMP_FORMAT)
        return doc


class Employee(Base):
    __tablename__ = 'employees'

    id = Column(Integer, primary_key=True)

    checks = relationship("EmployeePayment", back_populates="employee", cascade="all, delete, delete-orphan")
    memos = relationship("EmployeeMemo", back_populates="employee", cascade="all, delete, delete-orphan")
    # delete cascade does not work on Contracts
    contracts = relationship("Contract", back_populates="employee", cascade="all, delete, delete-orphan")
    comm_items = relationship("Citem", back_populates="employee", cascade="all, delete, delete-orphan")
    cnotes = relationship("Note", back_populates="employee", cascade="all, delete, delete-orphan")
    notes_payments = relationship("NotePayment", back_populates="employee", cascade="all, delete, delete-orphan")

    active = Column(Boolean)

    firstname = Column(String(20))
    lastname = Column(String(20))
    mi = Column(String(2))
    nickname = Column(String(20))
    street1 = Column(String(40))
    street2 = Column(String(40))
    city = Column(String(20))

    state_id = Column(Integer, ForeignKey('states.id'))
    state = relationship("State")

    zip = Column(String(10))
    ssn_crypto = Column(String(255))
    bankaccountnumber_crypto = Column(String(255))
    bankaccounttype = Column(String(8))
    bankname = Column(String(35))
    bankroutingnumber_crypto = Column(String(255))

    directdeposit = Column(Boolean)
    allowancefederal = Column(Integer)
    allowancestate = Column(Integer)
    extradeductionfed = Column(Integer)
    extradeductionstate = Column(Integer)
    maritalstatusfed = Column(String(40))
    maritalstatusstate = Column(String(40))
    usworkstatus = Column(Integer)
    notes = Column(TEXT)
    tcard = Column(Boolean)
    voided = Column(Boolean, default=False)
    w4 = Column(Boolean)
    de34 = Column(Boolean)
    i9 = Column(Boolean)
    medical = Column(Boolean)
    indust = Column(Boolean)
    info = Column(Boolean)
    phone = Column(String(100))
    dob = Column(Date)
    salesforce = Column(Boolean)

    voided = Column(Boolean, default=False)

    startdate = Column(Date)
    enddate = Column(Date)
    created_date = Column(Date, default=default_date)
    modified_date = Column(DateTime, default=func.now(), onupdate=func.now())
    created_user_id = Column(Integer)
    modified_user_id = Column(Integer)
    last_sync_time = Column(TIMESTAMP)

    def __repr__(self):
        return "<Employee(id='%s', firstname='%s', lastname='%s')>" % (
            self.id, self.firstname, self.lastname)

    def to_xml(self, crypter):
        if self.ssn_crypto:
            ssn_crypto = crypter.Decrypt(self.ssn_crypto)
        else:
            ssn_crypto = None
        if self.bankaccountnumber_crypto:
            bankaccountnumber_crypto = crypter.Decrypt(self.bankaccountnumber_crypto)
        else:
            bankaccountnumber_crypto = None
        if self.bankroutingnumber_crypto:
            bankroutingnumber_crypto = crypter.Decrypt(self.bankroutingnumber_crypto)
        else:
            bankroutingnumber_crypto = None

        doc = ET.Element('employee')
        ET.SubElement(doc, 'id').text = str(self.id)
        ET.SubElement(doc, 'firstname').text = self.firstname
        ET.SubElement(doc, 'lastname').text = self.lastname
        ET.SubElement(doc, 'mi').text = self.mi
        ET.SubElement(doc, 'nickname').text = self.nickname
        ET.SubElement(doc, 'street1').text = self.street1
        ET.SubElement(doc, 'street2').text = self.street2
        ET.SubElement(doc, 'city').text = self.city
        ET.SubElement(doc, 'state').text = str(self.state.name)
        ET.SubElement(doc, 'zip').text = self.zip
        ET.SubElement(doc, 'ssn_crypto').text = ssn_crypto
        ET.SubElement(doc, 'bankaccountnumber_crypto').text = bankaccountnumber_crypto
        ET.SubElement(doc, 'bankaccounttype').text = self.bankaccounttype
        ET.SubElement(doc, 'bankroutingnumber_crypto').text = bankroutingnumber_crypto
        ET.SubElement(doc, 'directdeposit').text = str(self.directdeposit)
        ET.SubElement(doc, 'allowancefederal').text = str(self.allowancefederal)
        ET.SubElement(doc, 'allowancestate').text = str(self.allowancestate)
        ET.SubElement(doc, 'extradeductionfed').text = str(self.extradeductionfed)
        ET.SubElement(doc, 'extradeductionstate').text = str(self.extradeductionstate)
        ET.SubElement(doc, 'maritalstatusfed').text = self.maritalstatusfed
        ET.SubElement(doc, 'maritalstatusstate').text = self.maritalstatusstate
        ET.SubElement(doc, 'usworkstatus').text = str(self.usworkstatus)
        ET.SubElement(doc, 'notes').text = re.sub(r'[^\x00-\x7F]', ' ', self.notes) if self.notes else ''
        ET.SubElement(doc, 'state_id').text = str(self.state_id)
        ET.SubElement(doc, 'salesforce').text = str(self.salesforce)
        ET.SubElement(doc, 'active').text = str(self.active)
        ET.SubElement(doc, 'tcard').text = str(self.tcard)
        ET.SubElement(doc, 'w4').text = str(self.w4)
        ET.SubElement(doc, 'de34').text = str(self.de34)
        ET.SubElement(doc, 'i9').text = str(self.i9)
        ET.SubElement(doc, 'medical').text = str(self.medical)
        ET.SubElement(doc, 'voided').text = str(self.voided)
        ET.SubElement(doc, 'indust').text = str(self.indust)
        ET.SubElement(doc, 'info').text = str(self.info)
        ET.SubElement(doc, 'phone').text = re.sub(r'[^\x00-\x7F]', ' ', self.phone) if self.phone else ''
        ET.SubElement(doc, 'dob').text = dt.strftime(self.dob, TIMESTAMP_FORMAT) if self.dob else dt.strftime(dt.now(),
                                                                                                              TIMESTAMP_FORMAT)
        ET.SubElement(doc, 'startdate').text = dt.strftime(self.startdate,
                                                           TIMESTAMP_FORMAT) if self.startdate else dt.strftime(
            dt.now(),
            TIMESTAMP_FORMAT)
        ET.SubElement(doc, 'enddate').text = dt.strftime(self.enddate,
                                                         TIMESTAMP_FORMAT) if self.enddate else dt.strftime(
            dt.now(), TIMESTAMP_FORMAT)

        checks = ET.Element('employee-payments')
        for o in self.checks:
            checks.append(o.to_xml(crypter))
        doc.append(checks)
        memos = ET.Element('memos')
        for o in self.memos:
            memos.append(o.to_xml(crypter))
        doc.append(memos)

        ET.SubElement(doc, 'contracts')

        comm_items = ET.Element('employee-commissions-items')
        for o in self.comm_items:
            comm_items.append(o.to_xml(crypter))
        doc.append(comm_items)
        cnotes = ET.Element('employee-commissions-notes')
        for o in self.cnotes:
            cnotes.append(o.to_xml(crypter))
        doc.append(cnotes)
        notes_payments = ET.Element('employee-notes-payments')
        for o in self.notes_payments:
            notes_payments.append(o.to_xml(crypter))
        doc.append(notes_payments)

        return doc

    @staticmethod
    def from_xml(xml_file_name):
        """                                                                                                                    
        returns DOM of comm item from file                                                                                     
        """
        return ET.parse(xml_file_name).getroot()

    def update_from_xml_doc(self, emp_doc, crypter):
        self.firstname = emp_doc.findall('firstname')[0].text
        self.lastname = emp_doc.findall('lastname')[0].text
        if emp_doc.findall('ssn_crypto')[0].text:
            self.ssn_crypto = crypter.Encrypt(emp_doc.findall('ssn_crypto')[0].text)
        else:
            self.ssn_crypto = crypter.Encrypt('N/A')
        if emp_doc.findall('bankaccountnumber_crypto')[0].text:
            self.bankaccountnumber_crypto = crypter.Encrypt(emp_doc.findall('bankaccountnumber_crypto')[0].text)
        else:
            self.bankaccountnumber_crypto = crypter.Encrypt('N/A')
        if emp_doc.findall('bankroutingnumber_crypto')[0].text:
            self.bankroutingnumber_crypto = crypter.Encrypt(emp_doc.findall('bankroutingnumber_crypto')[0].text)
        else:
            self.bankroutingnumber_crypto = crypter.Encrypt('N/A')


def delete_employee(session, delemp):
    """
    delete cascade to contracts does not work, contracts must be deleted first
    :param session:
    :param delemp:
    :return:
    """
    for con in session.query(Contract).filter(Contract.employee_id == delemp.id):
        session.delete(con)
    session.delete(delemp)


class NotePayment(Base):
    __tablename__ = 'notes_payments'

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey('employees.id'))
    employee = relationship("Employee")
    check_number = Column(String(25))
    date = Column(Date, index=True)
    amount = Column(Float)
    notes = Column(String(100))
    voided = Column(Boolean, default=False)
    created_date = Column(Date, default=default_date)
    modified_date = Column(DateTime, default=func.now(), onupdate=func.now())
    modified_user_id = Column(Integer)
    created_user_id = Column(Integer)

    def __repr__(self):
        return "<NotePayment(id='%s', employee='%s %s', check_number='%s', date='%s', amount='%s', notes='%s')>" % (
            self.id, self.employee.firstname, self.employee.lastname,
            self.check_number, self.date, self.amount,
            self.notes)

    def to_xml(self, crypter):
        doc = ET.Element('notes-payment')
        ET.SubElement(doc, 'id').text = str(self.id)
        ET.SubElement(doc, 'employee_id').text = str(self.employee_id)
        ET.SubElement(doc, 'check_number').text = self.check_number
        ET.SubElement(doc, 'date').text = dt.strftime(self.date, TIMESTAMP_FORMAT) if self.date else dt.strftime(
            dt.now(), TIMESTAMP_FORMAT)
        ET.SubElement(doc, 'amount').text = str(self.amount)
        ET.SubElement(doc, 'notes').text = re.sub(r'[^\x00-\x7F]', ' ', self.notes) if self.notes else ''
        ET.SubElement(doc, 'voided').text = str(self.voided)
        return doc


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
    voided = Column(Boolean, default=False)
    cleared = Column(Boolean, default=False)
    created_date = Column(Date, default=default_date)
    modified_date = Column(DateTime, default=func.now(), onupdate=func.now())
    modified_user_id = Column(Integer)
    created_user_id = Column(Integer)

    def to_xml(self, crypter):
        doc = ET.Element('note')
        ET.SubElement(doc, 'id').text = str(self.id)
        ET.SubElement(doc, 'date').text = dt.strftime(self.date, TIMESTAMP_FORMAT) if self.date else dt.strftime(
            dt.now(), TIMESTAMP_FORMAT)
        ET.SubElement(doc, 'amount').text = str(self.amount)
        ET.SubElement(doc, 'notes').text = re.sub(r'[^\x00-\x7F]', ' ', self.notes) if self.notes else ''
        ET.SubElement(doc, 'employee_id').text = str(self.employee_id)
        ET.SubElement(doc, 'commissions_payment_id').text = str(self.commissions_payment_id)
        ET.SubElement(doc, 'opening').text = str(self.opening)
        ET.SubElement(doc, 'voided').text = str(self.voided)
        ET.SubElement(doc, 'cleared').text = str(self.cleared)
        return doc


class CommPayment(Base):
    __tablename__ = 'commissions_payments'

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey('employees.id'))
    employee = relationship("Employee")
    date = Column(Date, index=True, default=default_date, nullable=False)
    amount = Column(Float)
    description = Column(TEXT)
    check_number = Column(String(10))
    cleared = Column(Boolean, default=False)
    voided = Column(Boolean, default=False)

    # fixme: add last_sync_time

    def __repr__(self):
        return "<CommissionsPayment(id='%s', employee='%s %s', check_number='%s', date='%s', amount='%s'," \
               " description='%s')>" % (
                   self.id, self.employee.firstname, self.employee.lastname,
                   self.check_number, self.date, self.amount,
                   self.description)

    def to_xml(self, crypter):
        doc = ET.Element('commissions-payment')
        ET.SubElement(doc, 'id').text = str(self.id)
        ET.SubElement(doc, 'employee_id').text = str(self.employee.id)
        ET.SubElement(doc, 'amount').text = str(self.amount)
        ET.SubElement(doc, 'check_number').text = str(self.check_number)
        ET.SubElement(doc, 'description').text = str(self.description)
        ET.SubElement(doc, 'cleared').text = str(self.cleared)
        ET.SubElement(doc, 'voided').text = str(self.voided)
        ET.SubElement(doc, 'date').text = dt.strftime(self.date, TIMESTAMP_FORMAT)
        return doc

    @staticmethod
    def from_xml(xml_file_name):
        """
        returns DOM of comm item from file
        """
        return ET.parse(xml_file_name).getroot()


class Client(Base):
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True)

    contracts = relationship("Contract", back_populates="client", cascade="all, delete, delete-orphan")
    checks = relationship("ClientCheck", back_populates="client", cascade="all, delete, delete-orphan")
    memos = relationship("ClientMemo", back_populates="client", cascade="all, delete, delete-orphan")

    name = Column(String(50))
    street1 = Column(String(50))
    street2 = Column(String(50))
    city = Column(String(50))

    state_id = Column(Integer, ForeignKey('states.id'))
    state = relationship("State")
    zip = Column(String(50))
    active = Column(Boolean)
    terms = Column(Integer, nullable=False)
    hq = Column(Boolean)
    modified_date = Column(DateTime, default=func.now(), onupdate=func.now())
    created_date = Column(Date, default=default_date)
    modified_date = Column(DateTime, default=func.now(), onupdate=func.now())
    created_user = Column(Integer)
    last_sync_time = Column(Date)

    def __repr__(self):
        return "<Client(id='%s', name='%s', street1='%s', street2='%s', state_id='%s', zip='%s', terms='%s', active='%s'" \
               ")>" % (self.id, self.name, self.street1, self.street2, self.state_id, self.zip, self.terms, self.active)

    def to_xml(self, crypter):
        doc = ET.Element('client')
        ET.SubElement(doc, 'id').text = str(self.id)
        ET.SubElement(doc, 'name').text = self.name
        ET.SubElement(doc, 'street1').text = self.street1
        ET.SubElement(doc, 'street2').text = self.street2
        ET.SubElement(doc, 'state_id').text = str(self.state_id)
        ET.SubElement(doc, 'zip').text = self.zip
        ET.SubElement(doc, 'terms').text = str(self.terms)
        ET.SubElement(doc, 'active').text = str(self.active)

        checks = ET.Element('checks')
        for o in self.checks:
            checks.append(o.to_xml(crypter))
        doc.append(checks)
        memos = ET.Element('memos')
        for o in self.memos:
            memos.append(o.to_xml(crypter))
        doc.append(memos)
        ET.SubElement(doc, 'contracts')
        return doc


class ClientMemo(Base):
    __tablename__ = 'clients_memos'

    id = Column(Integer, primary_key=True)

    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    client = relationship("Client")

    notes = Column(String(100))
    date = Column(Date, nullable=False)
    created_date = Column(Date, default=default_date)
    modified_date = Column(DateTime, default=func.now(), onupdate=func.now())
    created_user_id = Column(Integer)
    modified_user_id = Column(Integer)
    last_sync_time = Column(TIMESTAMP)

    def __repr__(self):
        return "<ClientMemo(id='%s', client='%s', date='%s', notes='%s')>" % (
            self.id, self.client.name, dt.strftime(self.date, TIMESTAMP_FORMAT), self.notes)

    def to_xml(self, crypter):
        doc = ET.Element('memo')
        ET.SubElement(doc, 'id').text = str(self.id)
        ET.SubElement(doc, 'client_id').text = str(self.client_id)
        ET.SubElement(doc, 'notes').text = str(self.notes)
        ET.SubElement(doc, 'date').text = dt.strftime(self.date, TIMESTAMP_FORMAT)
        return doc


class ClientManager(Base):
    __tablename__ = 'clients_managers'

    id = Column(Integer, primary_key=True)

    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    client = relationship("Client")

    firstname = Column(String(50))
    lastname = Column(String(50))
    phone1 = Column(String(50))
    phone2 = Column(String(50))
    phone1type = Column(String(50))
    phone2type = Column(String(50))
    title = Column(String(50))
    created_date = Column(Date, default=default_date)
    modified_date = Column(DateTime, default=func.now(), onupdate=func.now())
    created_user_id = Column(Integer)
    modified_user_id = Column(Integer)
    last_sync_time = Column(TIMESTAMP)

    def __repr__(self):
        return "<ClientManager(id='%s', client='%s', firstname='%s', lastname='%s')>" % (
            self.id, self.client.name, self.firstname, self.lastname)

    def to_xml(self, crypter):
        doc = ET.Element('manager')
        ET.SubElement(doc, 'id').text = str(self.id)
        ET.SubElement(doc, 'client_id').text = str(self.client_id)
        ET.SubElement(doc, 'title').text = self.title
        ET.SubElement(doc, 'firstname').text = self.title
        ET.SubElement(doc, 'lastname').text = self.title
        ET.SubElement(doc, 'phone1').text = self.title
        ET.SubElement(doc, 'phone2').text = self.title
        ET.SubElement(doc, 'phone1type').text = self.title
        ET.SubElement(doc, 'phone2type').text = self.title
        return doc


class ClientCheck(Base):
    __tablename__ = 'clients_checks'

    id = Column(Integer, primary_key=True)

    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    client = relationship("Client")

    invoice_payments = relationship("InvoicePayment", back_populates="check", cascade="all, delete, delete-orphan")
    number = Column(String(20))
    amount = Column(Float)
    notes = Column(String(100))

    date = Column(Date, nullable=False)
    created_date = Column(Date, default=default_date)
    modified_date = Column(DateTime, default=func.now(), onupdate=func.now())
    created_user_id = Column(Integer)
    modified_user_id = Column(Integer)
    last_sync_time = Column(TIMESTAMP)

    def __repr__(self):
        return "<ClientCheck(id='%s', client='%s', amount='%s', number='%s', date='%s')>" % (
            self.id, self.client.name, self.amount, self.number, self.date)

    def to_xml(self, crypter):
        doc = ET.Element('check')
        ET.SubElement(doc, 'id').text = str(self.id)
        ET.SubElement(doc, 'client_id').text = str(self.client_id)
        ET.SubElement(doc, 'number').text = str(self.number)
        ET.SubElement(doc, 'amount').text = str(self.amount)
        ET.SubElement(doc, 'notes').text = str(self.notes)
        ET.SubElement(doc, 'date').text = dt.strftime(self.date, TIMESTAMP_FORMAT)
        return doc


class ContractItemCommItem(Base):
    """

    """
    __tablename__ = 'contracts_items_commissions_items'

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    employee = relationship("Employee")

    contract_item_id = Column(Integer, ForeignKey('contracts_items.id'), nullable=False)
    contract_item = relationship("ContractItem")

    percent = Column(Float)
    modified_date = Column(DateTime, default=func.now(), onupdate=func.now())
    created_date = Column(Date, default=default_date)
    modified_date = Column(DateTime, default=func.now(), onupdate=func.now())
    created_user_id = Column(Integer)

    def __repr__(self):
        return "<ContractItemCommItem(id='%s', contract_title='%s', " \
               "salesperson='%s')>" % (
                   self.id, self.contract_item.contract.title,
                   '%s %s' % (self.employee.firstname, self.employee.lastname))

    def to_xml(self, crypter):
        doc = ET.Element('contract-commissions-item')
        ET.SubElement(doc, 'id').text = str(self.id)
        ET.SubElement(doc, 'employee_id').text = str(self.employee_id)
        ET.SubElement(doc,
                      'employee_firstname').text = self.employee.firstname if self.employee and self.employee.firstname else ''
        ET.SubElement(doc,
                      'employee_lastname').text = self.employee.lastname if self.employee and self.employee.lastname else ''
        ET.SubElement(doc, 'contract_item_id').text = str(self.contract_item_id)
        ET.SubElement(doc, 'percent').text = str(self.percent)
        return doc


class ContractItem(Base):
    __tablename__ = 'contracts_items'

    id = Column(Integer, primary_key=True)
    active = Column(Boolean)

    contract_id = Column(Integer, ForeignKey('clients_contracts.id'), nullable=False)
    contract = relationship("Contract")

    contract_comm_items = relationship(
        "ContractItemCommItem", back_populates="contract_item", cascade="all, delete, delete-orphan")

    amt = Column(Float)
    cost = Column(Float)
    description = Column(TEXT)

    notes = Column(TEXT)
    created_date = Column(Date, default=default_date)
    modified_date = Column(DateTime, default=func.now(), onupdate=func.now())
    modified_user_id = Column(Integer)
    created_user_id = Column(Integer)
    last_sync_time = Column(Date)

    def __repr__(self):
        return "<ContractItem(id='%s', description='%s')>" % (self.id, self.description)

    def to_xml(self, crypter):
        doc = ET.Element('contract-item')
        ET.SubElement(doc, 'id').text = str(self.id)
        ET.SubElement(doc, 'active').text = str(self.active)
        ET.SubElement(doc, 'contract_id').text = str(self.contract_id)
        ET.SubElement(doc, 'amt').text = str(self.amt)
        ET.SubElement(doc, 'cost').text = str(self.cost)
        ET.SubElement(doc, 'description').text = re.sub(r'[^\x00-\x7F]', ' ',
                                                        self.description) if self.description else ''
        ET.SubElement(doc, 'notes').text = re.sub(r'[^\x00-\x7F]', ' ', self.notes) if self.notes else ''
        con_comm_items = ET.Element('contract-commissions-items')
        for o in self.contract_comm_items:
            con_comm_items.append(o.to_xml(crypter))
        doc.append(con_comm_items)
        return doc


class Contract(Base):
    __tablename__ = 'clients_contracts'

    id = Column(Integer, primary_key=True)

    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    client = relationship("Client")
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    employee = relationship("Employee")

    invoices = relationship("Invoice", back_populates="contract", cascade="all, delete, delete-orphan")
    contract_items = relationship("ContractItem", back_populates="contract", cascade="all, delete, delete-orphan")
    period_id = Column(Integer)
    active = Column(Boolean)
    notes = Column(TEXT)
    title = Column(TEXT)
    terms = Column(Integer, nullable=False)
    startdate = Column(Date)
    enddate = Column(Date)
    created_date = Column(Date, default=default_date)
    modified_date = Column(DateTime, default=func.now(), onupdate=func.now())
    modified_user_id = Column(Integer)
    created_user_id = Column(Integer)
    last_sync_time = Column(TIMESTAMP)

    def __repr__(self):
        if self.enddate:
            return "<Contract(id='%s', client=%s, title='%s', employee='%s %s', startdate='%s', enddate='%s')>" % (
                self.id, self.client.name, self.title, self.employee.firstname,
                self.employee.lastname, self.startdate, self.enddate)
        else:
            return "<Contract(id='%s', client=%s, title='%s', employee='%s %s', startdate='%s'>" % (
                self.id, self.client.name, self.title, self.employee.firstname,
                self.employee.lastname, self.startdate)

    def to_xml(self, crypter):
        doc = ET.Element('contract')
        ET.SubElement(doc, 'id').text = str(self.id)
        ET.SubElement(doc, 'title').text = re.sub(r'[^\x00-\x7F]', ' ', self.title) if self.title else ''
        ET.SubElement(doc, 'notes').text = re.sub(r'[^\x00-\x7F]', ' ', self.notes) if self.notes else ''
        ET.SubElement(doc, 'client_id').text = str(self.client_id)
        ET.SubElement(doc, 'client').text = self.client.name
        ET.SubElement(doc, 'employee_id').text = str(self.employee_id)
        ET.SubElement(doc, 'employee').text = ('%s %s' % (self.employee.firstname, self.employee.lastname))
        ET.SubElement(doc, 'period_id').text = str(self.period_id)
        ET.SubElement(doc, 'active').text = str(self.active)
        ET.SubElement(doc, 'terms').text = str(self.terms)
        ET.SubElement(doc, 'startdate').text = dt.strftime(self.startdate, TIMESTAMP_FORMAT)
        ET.SubElement(doc, 'enddate').text = dt.strftime(self.enddate,
                                                         TIMESTAMP_FORMAT) if self.enddate else dt.strftime(dt.now(),
                                                                                                            TIMESTAMP_FORMAT)
        ET.SubElement(doc, 'invoices')
        contract_items = ET.Element('contract-items')
        for o in self.contract_items:
            contract_items.append(o.to_xml(crypter))
        doc.append(contract_items)
        return doc


class InvoicePayment(Base):
    __tablename__ = 'invoices_payments'

    id = Column(Integer, primary_key=True)

    invoice_id = Column(Integer, ForeignKey('invoices.id'), nullable=False)
    invoice = relationship("Invoice", back_populates='invoice_payments')

    check_id = Column(Integer, ForeignKey('clients_checks.id'), nullable=False)
    check = relationship("ClientCheck", back_populates='invoice_payments')

    amount = Column(Float)
    notes = Column(String(100))

    created_date = Column(Date, default=default_date)
    modified_date = Column(DateTime, default=func.now(), onupdate=func.now())
    created_user_id = Column(Integer)
    modified_user_id = Column(Integer)
    last_sync_time = Column(TIMESTAMP)

    def __repr__(self):
        return "<InvoicePayment(id='%s', invoice='%s', amount='%s', number='%s', date='%s')>" % (
            self.id, self.invoice_id, self.amount, self.check.number, self.check.date)

    def to_xml(self, crypter):
        doc = ET.Element('invoice-payment')
        ET.SubElement(doc, 'id').text = str(self.id)
        ET.SubElement(doc, 'invoice_id').text = str(self.invoice_id)
        ET.SubElement(doc, 'check_id').text = str(self.check_id)
        ET.SubElement(doc, 'amount').text = str(self.amount)
        ET.SubElement(doc, 'notes').text = str(self.notes)
        return doc


class Invoice(Base):
    __tablename__ = 'invoices'

    id = Column(Integer, primary_key=True)

    contract_id = Column(Integer, ForeignKey('clients_contracts.id'), nullable=False)

    contract = relationship("Contract", backref="clients_contracts")

    invoice_items = relationship("Iitem", back_populates="invoice", cascade="all, delete, delete-orphan")
    invoice_payments = relationship("InvoicePayment", back_populates="invoice", cascade="all, delete, delete-orphan")
    employee_payments = relationship("EmployeePayment", back_populates="invoice", cascade="all, delete, delete-orphan")

    date = Column(Date, nullable=False)

    po = Column(String(30))
    employerexpenserate = Column(Float)
    terms = Column(Integer, nullable=False)
    timecard = Column(Boolean)
    notes = Column(String(160))
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)

    posted = Column(Boolean)
    cleared = Column(Boolean, default=False)
    cleared_date = Column(Date)
    prcleared = Column(Boolean, default=False)
    timecard_receipt_sent = Column(Boolean)
    message = Column(TEXT)

    amount = Column(Float)
    voided = Column(Boolean, default=False)

    token = Column(String(64))
    view_count = Column(Integer)
    mock = Column(Boolean)
    created_date = Column(Date, default=default_date)
    modified_date = Column(DateTime, default=func.now(), onupdate=func.now())
    created_user_id = Column(Integer)
    modified_user_id = Column(Integer)
    last_sync_time = Column(DateTime)

    def __repr__(self):
        return "<Invoice(id='%s', client='%s', contract='%s', amount='%s', worker='%s'" \
               "duedate='%s', period_start='%s', " \
               "period_end='%s', date='%s', voided='%s')>" % (
                   self.id, self.contract.client.name, self.contract.title, self.amount, '%s %s' % (
                       self.contract.employee.firstname, self.contract.employee.lastname), self.duedate(),
                   self.period_start, self.period_end, self.date, self.voided)

    def duedate(self):
        return date_to_datetime(self.date) + td(days=self.terms)

    def to_xml(self, crypter):
        doc = ET.Element('invoice')

        ET.SubElement(doc, 'id').text = str(self.id)
        ET.SubElement(doc, 'contract_id').text = str(self.contract_id)
        ET.SubElement(doc, 'date').text = dt.strftime(self.date, TIMESTAMP_FORMAT)
        ET.SubElement(doc, 'po').text = str(self.po)
        ET.SubElement(doc, 'employerexpenserate').text = str(self.employerexpenserate)
        ET.SubElement(doc, 'terms').text = str(self.terms)
        ET.SubElement(doc, 'timecard').text = str(self.timecard)
        ET.SubElement(doc, 'notes').text = str(self.notes)
        ET.SubElement(doc, 'period_start').text = dt.strftime(self.period_start, TIMESTAMP_FORMAT)
        ET.SubElement(doc, 'period_end').text = dt.strftime(self.period_end, TIMESTAMP_FORMAT)
        ET.SubElement(doc, 'posted').text = str(self.posted)
        ET.SubElement(doc, 'cleared').text = str(self.cleared)
        ET.SubElement(doc, 'voided').text = str(self.voided)
        ET.SubElement(doc, 'prcleared').text = str(self.prcleared)
        ET.SubElement(doc, 'message').text = str(self.message)
        ET.SubElement(doc, 'amount').text = str(self.amount_calc())
        ET.SubElement(doc, 'created_date').text = dt.strftime(self.created_date, TIMESTAMP_FORMAT)
        ET.SubElement(doc, 'modified_date').text = dt.strftime(self.modified_date, TIMESTAMP_FORMAT)
        ET.SubElement(doc, 'created_user_id').text = str(self.created_user_id)
        ET.SubElement(doc, 'modified_user_id').text = str(self.modified_user_id)
        ET.SubElement(doc, 'due_date').text = dt.strftime(self.duedate(), TIMESTAMP_FORMAT)
        ET.SubElement(doc, 'date_generated').text = dt.strftime(dt.now(), TIMESTAMP_FORMAT)
        ET.SubElement(doc, 'employee').text = '%s %s' % \
                                              (self.contract.employee.firstname, self.contract.employee.lastname)
        iitems = ET.SubElement(doc, 'invoice-items')
        for i in self.invoice_items:
            iitems.append(i.to_xml(crypter))
        ipayments = ET.SubElement(doc, 'invoice-payments')
        for i in self.invoice_payments:
            ipayments.append(i.to_xml(crypter))
        epayments = ET.SubElement(doc, 'employee-payments')
        for i in self.employee_payments:
            epayments.append(i.to_xml(crypter))
        return doc

    def amount_calc(self):
        amount = 0
        for iitem in self.invoice_items:
            amount += iitem.amount * iitem.quantity
        return amount

    def update_commissions(self):
        employerexpenserate = self.employerexpenserate
        for invoice_item in self.invoice_items:
            inv_item_amount = invoice_item.amount
            inv_item_cost = invoice_item.cost
            inv_item_quantity = invoice_item.quantity
            for commissions_item in invoice_item.comm_items:
                percent = commissions_item.percent
                commissions_item.amount = commissions_calculation(inv_item_quantity, inv_item_amount, inv_item_cost,
                                                                  employerexpenserate, percent)

    @staticmethod
    def from_xml(xml_file_name):
        """
        returns DOM of Invoice from file
        """
        return ET.parse(xml_file_name).getroot()

    def update_from_xml_doc(self, inv_doc):
        self.date = inv_doc.findall('date')[0].text
        self.notes = inv_doc.findall('notes')[0].text
        self.message = inv_doc.findall('message')[0].text
        if inv_doc.findall('posted')[0].text == 'False':
            self.posted = False
        elif inv_doc.findall('posted')[0].text == 'True':
            self.posted = True
        self.period_start = inv_doc.findall('period_start')[0].text
        self.period_end = inv_doc.findall('period_end')[0].text


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


def invoice_archives(root, invoice_state='pastdue'):
    """
    returns xml invoice id list for invoice states 'pastdue', 'open', 'cleared' and 'all'
    """
    res = []
    for i in root.findall('./%s/invoice' % invoice_state):
        res.append(i.text)
    return res


class State(Base):
    """
    US States.  Employees, Vendors and Clients belong to a State for reporting purposes
    """
    __tablename__ = 'states'

    id = Column(Integer, primary_key=True)
    post_ab = Column(String(2))
    capital = Column(String(14))
    date = Column(String(10))
    flower = Column(String(27))
    name = Column(String(14))
    state_no = Column(String(9))
    last_sync_time = Column(TIMESTAMP)
    created_date = Column(Date, default=default_date)
    modified_date = Column(DateTime, default=func.now(), onupdate=func.now())
    created_user_id = Column(Integer)
    modified_user_id = Column(Integer)

    def __repr__(self):
        return "<State(id='%s', name='%s', post_ab='%s')>" % (self.id, self.name, self.post_ab)

    def to_xml(self, crypter):
        doc = ET.Element('state')

        ET.SubElement(doc, 'id').text = str(self.id)

        ET.SubElement(doc, 'post_ab').text = str(self.post_ab)
        ET.SubElement(doc, 'capital').text = str(self.capital)
        ET.SubElement(doc, 'date').text = str(self.date)
        ET.SubElement(doc, 'flower').text = str(self.flower)
        ET.SubElement(doc, 'name').text = str(self.name)
        ET.SubElement(doc, 'state_no').text = str(self.state_no)
        return doc


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
    cleared = Column(Boolean, default=False)
    comm_items = relationship("Citem", back_populates="invoices_item", cascade="all, delete, delete-orphan")

    created_date = Column(Date, default=default_date)
    modified_date = Column(DateTime, default=func.now(), onupdate=func.now())
    created_user_id = Column(Integer)
    modified_user_id = Column(Integer)
    last_sync_time = Column(TIMESTAMP)

    def __repr__(self):
        return "<InvoiceItem(id='%s', description='%s', amount='%s', quantity='%s', invoice.id='%s')>" % (
            self.id, self.description, self.amount, self.quantity,
            self.invoice_id)

    def to_xml(self, crypter):
        doc = ET.Element('invoice-item')

        ET.SubElement(doc, 'id').text = str(self.id)
        ET.SubElement(doc, 'invoice_id').text = str(self.invoice_id)
        ET.SubElement(doc, 'description').text = str(self.description)
        ET.SubElement(doc, 'amount').text = str(self.amount)
        ET.SubElement(doc, 'cost').text = str(self.cost)
        ET.SubElement(doc, 'quantity').text = str(self.quantity)
        ET.SubElement(doc, 'cleared').text = str(self.cleared)
        commitems = ET.SubElement(doc, 'commissions-items')
        for i in self.comm_items:
            commitems.append(i.to_xml(crypter))
        return doc

    def update_from_xml_doc(self, iitem_ele):
        self.quantity = iitem_ele.findall('quantity')[0].text


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

    description = Column(String(50))
    date = Column(Date, index=True, default=default_date)
    percent = Column(Float)
    amount = Column(Float)
    rel_inv_amt = Column(Float)
    rel_inv_line_item_amt = Column(Float)
    rel_item_amt = Column(Float)
    rel_item_quantity = Column(Float)
    rel_item_cost = Column(Float)
    cleared = Column(Boolean, default=False)
    voided = Column(Boolean, default=False)
    created_date = Column(Date, default=default_date)
    modified_date = Column(DateTime, default=func.now(), onupdate=func.now())
    created_user_id = Column(Integer, default=2)
    modified_user_id = Column(Integer, default=2)
    last_sync_time = Column(TIMESTAMP)

    def __repr__(self):
        return "<Citem(description='%s', id='%s', employee_id='%s', amount='%s'. mod_date='%s', " \
               "invoices_item_id='%s', invoice_id='%s', contract='%s', contract_id='%s')>" % (
                   self.description, self.id, self.employee_id, self.amount,
                   self.modified_date, self.invoices_item_id, self.invoices_item.invoice.id,
                   self.invoices_item.invoice.contract.title, self.invoices_item.invoice.contract.id)

    def to_xml(self, crypter):
        if self.invoices_item.amount and self.invoices_item.quantity:
            iitemamount = self.invoices_item.amount * self.invoices_item.quantity
        else:
            iitemamount = 0.0
        if self.invoices_item.cost and self.invoices_item.quantity:
            wage = self.invoices_item.cost * self.invoices_item.quantity
        else:
            wage = 0.0
        if self.invoices_item.cost and self.invoices_item.quantity:
            empexp = self.invoices_item.cost * self.invoices_item.quantity * .1
        else:
            empexp = 0.0

        doc = ET.Element('invoices-items-commissions-item')

        ET.SubElement(doc, 'id').text = str(self.id)
        ET.SubElement(doc, 'invoice_id').text = str(self.invoices_item.invoice_id)
        ET.SubElement(doc, 'employee_id').text = str(self.employee_id)
        ET.SubElement(doc, 'employee_firstname').text = str(
            self.employee.firstname) if self.employee and self.employee.firstname else ''
        ET.SubElement(doc, 'employee_lastname').text = str(
            self.employee.lastname) if self.employee and self.employee.lastname else ''

        ET.SubElement(doc, 'invoices_item_id').text = str(self.invoices_item_id)
        ET.SubElement(doc, 'description').text = '%s-%s %s' % (
            dt.strftime(self.invoices_item.invoice.period_start, YMD_FORMAT),
            dt.strftime(self.invoices_item.invoice.period_end, YMD_FORMAT),
            self.description)
        ET.SubElement(doc, 'date').text = dt.strftime(self.date, TIMESTAMP_FORMAT)
        ET.SubElement(doc, 'percent').text = str(self.percent)
        ET.SubElement(doc, 'amount').text = str((((iitemamount - wage - empexp) * self.percent) / 100))
        ET.SubElement(doc, 'rel_inv_amt').text = str(self.rel_inv_amt)
        ET.SubElement(doc, 'rel_inv_line_item_amt').text = str(self.rel_inv_line_item_amt)
        ET.SubElement(doc, 'rel_item_amt').text = str(self.rel_item_amt)
        ET.SubElement(doc, 'rel_item_quantity').text = str(self.rel_item_quantity)
        ET.SubElement(doc, 'rel_item_cost').text = str(self.rel_item_cost)
        ET.SubElement(doc, 'rel_item_amt').text = str(self.rel_item_amt)
        ET.SubElement(doc, 'cleared').text = str(self.cleared)
        ET.SubElement(doc, 'voided').text = str(self.voided)
        ET.SubElement(doc, 'date_generated').text = dt.strftime(dt.now(), TIMESTAMP_FORMAT)
        ET.SubElement(doc, 'created_date').text = dt.strftime(self.created_date,
                                                              TIMESTAMP_FORMAT) if self.created_date else dt.strftime(
            dt.now(), TIMESTAMP_FORMAT)
        ET.SubElement(doc, 'modified_date').text = dt.strftime(self.modified_date,
                                                               TIMESTAMP_FORMAT) if self.modified_date else dt.strftime(
            dt.now(), TIMESTAMP_FORMAT)
        ET.SubElement(doc, 'created_user_id').text = str(self.created_user_id)
        ET.SubElement(doc, 'modified_user_id').text = str(self.modified_user_id)
        return doc

    @staticmethod
    def from_xml(xml_file_name):
        """
        returns DOM of comm item from file
        """
        return ET.parse(xml_file_name).getroot()


class Payroll(Base):
    __tablename__ = 'payrolls'

    id = Column(Integer, primary_key=True)
    name = Column(String(72), nullable=False)

    checks = relationship("EmployeePayment", back_populates="payroll", cascade="all, delete, delete-orphan")
    notes = Column(TEXT, nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(Date, index=True, nullable=False, default=default_date, onupdate=default_date)

    created_date = Column(Date, default=default_date)
    modified_date = Column(DateTime, default=func.now(), onupdate=func.now())
    created_user_id = Column(Integer, default=2)
    modified_user_id = Column(Integer, default=2)
    last_sync_time = Column(TIMESTAMP)

    def to_xml(self, crypter):
        doc = ET.Element('payroll')
        ET.SubElement(doc, 'id').text = str(self.id)

        ET.SubElement(doc, 'notes').text = str(self.notes)
        ET.SubElement(doc, 'amount').text = str(self.amount)
        ET.SubElement(doc, 'date').text = dt.strftime(self.date if self.date else dt.now(), TIMESTAMP_FORMAT)

        checks = ET.Element('checks')
        for o in self.checks:
            checks.append(o.to_xml(crypter))
        doc.append(checks)
        return doc


class ExpenseCategory(Base):
    __tablename__ = 'expenses_categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(22))

    def to_xml(self, crypter):
        doc = ET.Element('expense-category')
        ET.SubElement(doc, 'id').text = str(self.id)
        ET.SubElement(doc, 'name').text = str(self.name)
        return doc


class Expense(Base):
    __tablename__ = 'expenses'

    id = Column(Integer, primary_key=True)

    amount = Column(Float)

    category_id = Column(Integer, ForeignKey('expenses_categories.id'), nullable=False)
    category = relationship("ExpenseCategory")

    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    employee = relationship("Employee")

    cleared = Column(Boolean, default=False)
    date = Column(Date, index=True, default=default_date)

    description = Column(String(45))
    notes = Column(String(200))

    created_date = Column(Date, default=default_date)
    modified_date = Column(DateTime, default=func.now(), onupdate=func.now())
    created_user_id = Column(Integer, default=2)
    modified_user_id = Column(Integer, default=2)
    last_sync_time = Column(TIMESTAMP)

    def to_xml(self, crypter):
        doc = ET.Element('expense')

        ET.SubElement(doc, 'id').text = str(self.id)

        ET.SubElement(doc, 'amount').text = str(self.amount)

        ET.SubElement(doc, 'category_id').text = str(self.category_id)
        ET.SubElement(doc, 'employee_id').text = str(self.employee_id)

        ET.SubElement(doc, 'cleared').text = str(self.cleared)
        ET.SubElement(doc, 'date').text = dt.strftime(self.date, TIMESTAMP_FORMAT) if self.date else dt.strftime(
            dt.now(), TIMESTAMP_FORMAT)

        ET.SubElement(doc, 'description').text = str(self.description)
        ET.SubElement(doc, 'notes').text = str(self.notes)
        ET.SubElement(doc, 'created_date').text = dt.strftime(self.created_date,
                                                              TIMESTAMP_FORMAT) if self.created_date else dt.strftime(
            dt.now(), TIMESTAMP_FORMAT)
        ET.SubElement(doc, 'modified_date').text = dt.strftime(self.modified_date,
                                                               TIMESTAMP_FORMAT) if self.modified_date else dt.strftime(
            dt.now(), TIMESTAMP_FORMAT)
        ET.SubElement(doc, 'created_user_id').text = str(self.created_user_id)
        ET.SubElement(doc, 'modified_user_id').text = str(self.modified_user_id)
        return doc


class Vendor(Base):
    __tablename__ = 'vendors'

    id = Column(Integer, primary_key=True)
    memos = relationship("VendorMemo", back_populates="vendor", cascade="all, delete, delete-orphan")
    name = Column(String(40))
    purpose = Column(String(60))
    street1 = Column(String(30))
    street2 = Column(String(30))
    city = Column(String(20))

    state_id = Column(Integer, ForeignKey('states.id'))
    state = relationship("State")

    zip = Column(String(50))
    active = Column(Boolean)

    ssn = Column(String(11))

    apfirstname = Column(String(31))
    aplastname = Column(String(11))

    apphonetype1 = Column(Integer)
    apphone1 = Column(String(32))
    apphonetype2 = Column(Integer)
    apphone2 = Column(String(32))
    accountnumber = Column(String(65))
    notes = Column(String(183))
    secretbits = Column(TEXT)
    created_date = Column(Date, default=default_date)
    modified_date = Column(DateTime, default=func.now(), onupdate=func.now())
    created_user_id = Column(Integer)
    modified_user_id = Column(Integer)
    last_sync_time = Column(DateTime)

    def to_xml(self, crypter):
        doc = ET.Element('vendor')
        ET.SubElement(doc, 'id').text = str(self.id)

        ET.SubElement(doc, 'name').text = self.name
        ET.SubElement(doc, 'purpose').text = self.purpose

        ET.SubElement(doc, 'street1').text = self.street1
        ET.SubElement(doc, 'street2').text = self.street2
        ET.SubElement(doc, 'city').text = self.city
        ET.SubElement(doc, 'state').text = str(self.state.name)
        ET.SubElement(doc, 'zip').text = self.zip
        ET.SubElement(doc, 'active').text = str(self.active)
        ET.SubElement(doc, 'ssn').text = str(self.ssn)
        ET.SubElement(doc, 'apfirstname').text = str(self.apfirstname)
        ET.SubElement(doc, 'aplastname').text = str(self.aplastname)
        ET.SubElement(doc, 'apphonetype1').text = str(self.apphonetype1)
        ET.SubElement(doc, 'apphone1').text = str(self.apphone1)
        ET.SubElement(doc, 'apphonetype2').text = str(self.apphonetype2)
        ET.SubElement(doc, 'apphone2').text = str(self.apphone2)
        ET.SubElement(doc, 'accountnumber').text = str(self.accountnumber)
        ET.SubElement(doc, 'notes').text = re.sub(r'[^\x00-\x7F]', ' ', self.notes) if self.notes else ''
        ET.SubElement(doc, 'secretbits').text = str(self.secretbits)

        ET.SubElement(doc, 'created_date').text = dt.strftime(self.created_date,
                                                              TIMESTAMP_FORMAT) if self.created_date else dt.strftime(
            dt.now(), TIMESTAMP_FORMAT)
        ET.SubElement(doc, 'modified_date').text = dt.strftime(self.modified_date,
                                                               TIMESTAMP_FORMAT) if self.modified_date else dt.strftime(
            dt.now(), TIMESTAMP_FORMAT)
        ET.SubElement(doc, 'created_user_id').text = str(self.created_user_id)
        ET.SubElement(doc, 'modified_user_id').text = str(self.modified_user_id)

        memos = ET.SubElement(doc, 'memo')
        for o in self.memos:
            memos.append(o.to_xml(crypter))
        doc.append(memos)
        return doc


class VendorMemo(Base):
    __tablename__ = 'vendors_memos'

    id = Column(Integer, primary_key=True)

    vendor_id = Column(Integer, ForeignKey('vendors.id'), nullable=False)
    vendor = relationship("Vendor")

    notes = Column(String(100))
    date = Column(Date, nullable=False)
    created_date = Column(Date, default=default_date)
    modified_date = Column(DateTime, default=func.now(), onupdate=func.now())
    created_user_id = Column(Integer)
    modified_user_id = Column(Integer)
    last_sync_time = Column(TIMESTAMP)

    def __repr__(self):
        return "<VendorMemo(id='%s', vendor='%s', date='%s', notes='%s')>" % (
            self.id, self.vendor.name, dt.strftime(self.date, TIMESTAMP_FORMAT), self.notes)

    def to_xml(self, crypter):
        doc = ET.Element('memo')
        ET.SubElement(doc, 'id').text = str(self.id)
        ET.SubElement(doc, 'vendor_id').text = str(self.vendor_id)
        ET.SubElement(doc, 'notes').text = re.sub(r'[^\x00-\x7F]', ' ', self.notes) if self.notes else ''
        ET.SubElement(doc, 'date').text = dt.strftime(self.date, TIMESTAMP_FORMAT)
        return doc
