import os
import random
import string
from datetime import datetime as dt
from datetime import timedelta as td
from subprocess import call
from xml.dom import minidom as xml_pp
from xml.etree import ElementTree as ET

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tabulate import tabulate

from rrg.helpers import read_inv_xml_file
from rrg.lib.archive import full_non_dated_xml_obj_path
from rrg.models import Iitem, InvoicePayment, ClientManager, ClientCheck, ClientMemo, Employee, EmployeeMemo, \
    EmployeePayment, ContractItem, Citem, CommPayment, Expense, Payroll, Vendor
from rrg.models import Invoice, Client, Contract, State
from rrg import utils

def obj_dir(datadir, obj):
    """
    central place to generate archive directories paths
    :param datadir:
    :param obj:
    :return:
    """

    if isinstance(obj, type(Invoice())):
        return os.path.join(datadir, 'transactions', 'invoices')
    elif isinstance(obj, type(Iitem())):
        return os.path.join(os.path.join(datadir, 'transactions', 'invoices'), 'invoice_items')
    elif isinstance(obj, type(InvoicePayment())):
        return os.path.join(os.path.join(datadir, 'transactions', 'invoices'), 'invoice_payments')
    elif isinstance(obj, type(Client())):
        return os.path.join(datadir, 'clients')
    elif isinstance(obj, type(ClientManager())):
        return os.path.join(os.path.join(datadir, 'clients'), 'managers')
    elif isinstance(obj, type(ClientCheck())):
        return os.path.join(datadir, 'transactions', 'checks')
    elif isinstance(obj, type(ClientMemo())):
        return os.path.join(os.path.join(datadir, 'clients'), 'memos')
    elif isinstance(obj, type(Employee())):
        return os.path.join(datadir, 'employees')
    elif isinstance(obj, type(EmployeeMemo())):
        return os.path.join(datadir, 'employees', 'memos')
    elif isinstance(obj, type(EmployeePayment())):
        return os.path.join(datadir, 'employees', 'payments')
    elif isinstance(obj, type(Contract())):
        return os.path.join(datadir, 'contracts')
    elif isinstance(obj, type(ContractItem())):
        return os.path.join(datadir, 'contracts', 'contract_items')
    elif isinstance(obj, type(Citem())):
        return os.path.join(datadir, 'transactions', 'invoices', 'invoice_items', 'commissions_items')
    elif isinstance(obj, type(CommPayment())):
        return os.path.join(datadir, 'transactions', 'invoices', 'invoice_items', 'commissions_payments')
    elif isinstance(obj, type(Expense())):
        return os.path.join(datadir, 'expenses')
    elif isinstance(obj, type(Payroll())):
        return os.path.join(datadir, 'payrolls')
    elif isinstance(obj, type(State())):
        return os.path.join(datadir, 'states')
    elif isinstance(obj, type(Vendor())):
        return os.path.join(datadir, 'vendors')


def open_invoices(session):
    """
    return list of OPEN invoices
    """
    return session.query(Invoice).filter(
        Invoice.voided==False, Invoice.posted==True, Invoice.cleared==False, Invoice.mock == False, Invoice.amount > 0)



def timecards(session):
    """
    return list of timecards pending posting
    """
    return session.query(Invoice).filter(
        Invoice.voided==False, Invoice.posted==False, Invoice.cleared==False, Invoice.mock == False, Invoice.amount > 0)


def pastdue_invoices(session):
    """
    return list of PastDue invoices
    """
    res = []
    oinvs = open_invoices(session)
    for oi in oinvs:
        if Invoice.duedate(oi) <= dt.now():
            res.append(oi)
    return res


def picked_open_invoice(session, args):
    o_invoices = open_invoices(session)
    return o_invoices[args.number-1]


def tabulate_invoices(invoices):
    """
    Return given invoices list tabulated
    :param invoices:
    :return:
    """
    tbl = []
    i = 1
    for r in invoices:
        tbl.append(
            [i, r.id, r.contract.client.name, r.contract.employee.firstname + ' ' +
             r.contract.employee.lastname,
             dt.strftime(r.period_start, '%m/%d/%Y'), dt.strftime(r.period_end, '%m/%d/%Y'),
             r.date, r.date + td(days=r.contract.terms), r.amount])
        i += 1
    return tabulate(tbl, headers=['number', 'sqlid', 'client', 'employee', 'start', 'end', 'date', 'duedate', 'amount'])


def edit_invoice(session, phase, number):

    if phase == 'open':
        winvoices = open_invoices(session)
    elif phase =='timecard':
        winvoices = timecards(session)
    if number in range(1, winvoices.count() + 1):
        if phase == 'open':
            invoice = picked_open_invoice(session, number)
        elif phase =='timecard':
            invoice = picked_timecard(session, number)
        xml = xml_pp.parseString(ET.tostring(invoice.to_xml()))
        temp_file = os.path.join(
            os.path.sep, 'tmp', ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(40)))
        with open(temp_file, 'w+b') as f:
            f.write(xml.toprettyxml())
        call(["vi", temp_file])
        whole_inv_xml = Invoice.from_xml(temp_file)

        invoice.update_from_xml_doc(whole_inv_xml)

        for iitem in whole_inv_xml.iter('invoice-item'):
            iid = int(iitem.findall('id')[0].text)
            sa_item = session.query(Iitem).get(iid)
            sa_item.update_from_xml_doc(iitem)

        session.commit()
    else:
        print('Invoice number is not in range')
        quit()


def employees(session):
    """
    return list of all employees
    """
    return session.query(Employee)


def employees_active(session):
    """
    return list of active employees
    """
    return session.query(Employee).filter(Employee.active==True)


def employees_inactive(session):
    """
    return list of inactive employees
    """
    return session.query(Employee).filter(Employee.active==False)


def picked_employee(session, number):
    all_employees = session.query(Employee).all()
    return all_employees[number-1]


def edit_employee_script(session, number):
    """
    Running dialog script for editing an employee
    :param session:

    :param number:
    :return:
    """
    w_employees = employees.employees(session)

    if number in range(1, w_employees.count() + 1):

        employee = employees.picked_employee(session, number)
        xml = xml_pp.parseString(ET.tostring(employee.to_xml()))
        temp_file = os.path.join(
            os.path.sep, 'tmp', ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(40)))
        with open(temp_file, 'w+b') as f:
            f.write(xml.toprettyxml())
        call(["vi", temp_file])
        whole_emp_xml = Employee.from_xml(temp_file)

        employee.update_from_xml_doc(whole_emp_xml)

        session.commit()
    else:
        print('Employee number is not in range')
        quit()


def open_timecards(session):
    """
    return list of timecards from reminders
    """
    return session.query(Invoice).filter(Invoice.voided==False, Invoice.posted==False)


def picked_timecard(session, number):
    timecards = session.query(Invoice).filter(Invoice.voided==False, Invoice.posted==False)
    return timecards[number-1]


def void_timecard(session, number):
    timecards = session.query(Invoice).filter(Invoice.voided==False, Invoice.posted==False)
    timecard_to_void = timecards[number-1]
    timecard_to_void.voided = True


def clients_ar_xml_file(datadir):
    return os.path.join(os.path.join(datadir, 'transactions', 'invoices'), 'ar.xml')


def commissions_payment_dir(datadir, comm_payment):
    return obj_dir(datadir, comm_payment) + utils.employee_dated_object_reldir(comm_payment)


def generate_ar_report(app, type):
    print('Generating %s Report' % type)
    infile = clients_ar_xml_file(app.config['DATADIR'])
    print('Parsing %s' % infile)
    results = []
    if os.path.isfile(infile):
        tree = ET.parse(infile)
        root = tree.getroot()
        recs = invoice_archives(root, type)
        for i in recs:
            xmlpath = os.path.join(obj_dir(app.config['DATADIR'], Invoice()), '%05d.xml' % int(i))
            date, amount, employee, voided, terms, sqlid, client, duedate = read_inv_xml_file(xmlpath)
            if voided == 'False':
                results.append([amount, date, voided, employee, terms, sqlid, client, duedate])
    else:
        print('No AR.xml file found')
    return tabulate(results, headers=['amount', 'date', 'voided', 'employee', 'terms', 'sqlid', 'client', 'duedate'])


def _cache_obj(obj, full_path):
    if not os.path.isdir(os.path.dirname(full_path)):
        os.makedirs(os.path.dirname(full_path))
    with open(full_path, 'wb') as fh:
        fh.write(ET.tostring(obj.to_xml()))
    obj.last_sync_time = dt.now()
    print('%s written' % full_path)


def cache_objs(datadir, objs):
    for obj in objs:

        full_path = full_non_dated_xml_obj_path(obj_dir(datadir, obj), obj)
        if os.path.isfile(full_path):
            if obj.last_sync_time is None or obj.modified_date is None:
                _cache_obj(obj, full_path)
            elif obj.modified_date > obj.last_sync_time:
                _cache_obj(obj, full_path)
        else:
            _cache_obj(obj, full_path)


def invoice_archives(root, invoice_state='pastdue'):
    """
    returns xml invoice id list for invoice states 'pastdue', 'open', 'cleared' and 'all'
    """
    res = []
    for i in root.findall('./%s/invoice' % invoice_state):
        res.append(i.text)
    return res


def session_maker(db_user, db_pass, mysql_host, mysql_port, db):
    engine = create_engine(
        'mysql+mysqldb://%s:%s@%s:%s/%s' % (db_user, db_pass, mysql_host, mysql_port, db))

    session = sessionmaker(bind=engine)
    return session()


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