import os
import re
from datetime import datetime as dt
from tabulate import tabulate
import xml.etree.ElementTree as ET
import logging

from rrg.helpers import emp_xml_doc_to_dict
from rrg.helpers import emp_memo_xml_doc_to_dict
from rrg.helpers import emp_contract_xml_doc_to_dict
from rrg.helpers import emp_payment_xml_doc_to_dict
from rrg.models import Citem
from rrg.models import Client
from rrg.models import ClientCheck
from rrg.models import ClientManager
from rrg.models import ClientMemo
from rrg.models import CommPayment
from rrg.models import Contract
from rrg.models import ContractItem
from rrg.models import Employee
from rrg.models import EmployeePayment
from rrg.models import EmployeeMemo
from rrg.models import Expense
from rrg.models import Iitem
from rrg.models import Invoice
from rrg.models import InvoicePayment
from rrg.models import Payroll
from rrg.models import State
from rrg.models import Vendor

logging.basicConfig(filename='testing.log', level=logging.DEBUG)
logger = logging.getLogger('test')

logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

pat = '[0-9]{5}\.[xX][Mm][Ll]$'


def obj_dir(datadir, obj):
    """
    central place to generate archive directories
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


def full_non_dated_xml_id_path(data_dir, id):
    """
    generate xml path #####.xml from arbitrary object
    :param data_dir:
    :param id:
    :return:
    """
    return os.path.join(data_dir, '%s.xml' % str(id).zfill(5))


def full_non_dated_xml_obj_path(data_dir, obj):
    """
    generate xml path #####.xml from arbitrary object
    :param data_dir:
    :param obj:
    :return:
    """
    return os.path.join(data_dir, '%s.xml' % str(obj.id).zfill(5))


def full_dated_obj_xml_path(data_dir, obj):
    """
    generate xml path /year/month/primary_key.xml
    :param data_dir:
    :param obj:
    :return:
    used for commissions invoice items
    """
    rel_dir = os.path.join(str(obj.date.year), str(obj.date.month).zfill(2))
    return os.path.join(data_dir, rel_dir, '%s.xml' % str(obj.id).zfill(5)), rel_dir


def employee_dated_object_reldir(obj):
    return os.path.sep + os.path.join(str(obj.employee_id).zfill(5),
                                      str(obj.date.year),
                                      str(obj.date.month).zfill(2))
def employees(datadir):
    """
    return tabulated list of archived employees
    :param datadir:
    :return:
    """
    employees_directory = os.path.join(datadir, 'employees')
    ids = []
    sql_ids = []
    firsts = []
    lasts = []
    i = 1
    for root, dirs, files in os.walk(employees_directory):
        if root == employees_directory:
            print('root="%s"' % root)
            for f in files:
                if re.search(pat, f):
                    fullpath = os.path.join(root, f)
                    doc = ET.parse(fullpath).getroot()
                    firstname = doc.findall('firstname')[0].text
                    lastname = doc.findall('lastname')[0].text
                    ids.append(str(i))
                    sql_ids.append(int(doc.findall('id')[0].text))
                    firsts.append(firstname)
                    lasts.append(lastname)
                    i += 1
    res_dict_transposed = {
        'id': [i for i in ids],
        'sqlid': [i for i in sql_ids],
        'first': [i for i in firsts],
        'last': [i for i in lasts],
    }
    print(tabulate(res_dict_transposed, headers='keys', tablefmt='plain'))


def employee(id, datadir):
    employees_directory = os.path.join(datadir, 'employees')
    i = 1
    emp_dict = {
        'index': None,
        'id': None,
        'firstname': None,
        'lastname': None,
        'street1': None,
        'street2': None,
        'city': None,
        'state': None,
        'zip': None,
        'startdate': None,
        'enddate': None,
        'salesforce': False,
        'dob': None,
        'contracts': [], 'memos': [],
        'payments': [],
    }
    for root, dirs, files in os.walk(employees_directory):
        if root == employees_directory:
            for f in files:
                if re.search(pat, f):
                    if i == id:
                        doc = ET.parse(os.path.join(root, f)).getroot()
                        emp_dict = emp_xml_doc_to_dict(i, doc, emp_dict)
                        for eles in doc.findall('memos'):
                            for ele in eles.findall('memo'):
                                emp_dict['memos'].append(emp_memo_xml_doc_to_dict(ele))
                        for eles in doc.findall('contracts'):
                            for ele in eles.findall('contract'):
                                emp_dict['contracts'].append(emp_contract_xml_doc_to_dict(ele))
                        for eles in doc.findall('employee-payments'):
                            for ele in eles.findall('employee-payment'):
                                _ = full_non_dated_xml_id_path(os.path.join(datadir, 'employees', 'payments'), ele[0].text)
                                doc = ET.parse(_).getroot()
                                emp_dict['payments'].append(emp_payment_xml_doc_to_dict(doc))
                        break
                    i += 1
    return emp_dict


def contracts(datadir):
    contracts_directory = os.path.join(datadir, 'contracts')
    ids = []
    titles = []
    clients = []
    employees = []
    i = 1
    for root, dirs, files in os.walk(contracts_directory):
        if root == contracts_directory:
            print('root="%s"' % root)
            for f in files:
                if re.search(pat, f):
                    fullpath = os.path.join(root, f)
                    doc = ET.parse(fullpath).getroot()
                    title = doc.findall('title')[0].text
                    client = doc.findall('client')[0].text
                    employee = doc.findall('employee')[0].text
                    ids.append(str(i))
                    titles.append(title)
                    employees.append(employee)
                    clients.append(client)
                    i += 1
    res_dict_transposed = {
        'id': [i for i in ids],
        'titles': [i for i in titles],
        'clients': [i for i in clients],
        'employees': [i for i in employees],
    }
    print(tabulate(res_dict_transposed, headers='keys', tablefmt='plain'))


def contract(datadir, id):
    contracts_directory = os.path.join(datadir, 'contracts')
    i = 1
    for root, dirs, files in os.walk(contracts_directory):
        if root == contracts_directory:
            print('root="%s"' % root)
            for f in files:
                if re.search(pat, f):
                    if i == id:
                        fullpath = os.path.join(root, f)
                        doc = ET.parse(fullpath).getroot()
                        title = doc.findall('title')[0].text
                        client = doc.findall('client')[0].text
                        employee = doc.findall('employee')[0].text
                        print ('id="%s", title="%s", client="%s", employee="%s' % (i, title, client, employee))
                    i += 1


def doc_attach_collected_contracts(contract_doc_list):
    csub_ele = ET.Element('contracts')
    for idoc in contract_doc_list:
        csub_ele.append(idoc)

    return csub_ele


def contract_attach_collected_invoices(inv_doc_list):
    """
    attached contracts invoicers list gathered from disk
    :param contract_doc:
    :param inv_doc_list:
    :return:
    """
    isub_ele = ET.Element('invoices')

    for idoc in inv_doc_list:
        isub_ele.append(idoc)

    return isub_ele


def contract_attach_collected_contract_items(citem_doc_list):
    """
    attached contracts invoicers list gathered from disk
    :param contract_doc:
    :param citem_doc_list:
    :return:
    """
    isub_ele = ET.Element('contract-items')

    for idoc in citem_doc_list:
        isub_ele.append(idoc)

    return isub_ele


def cached_employees_collect_contracts(datadir):
    employees_directory = os.path.join(datadir, 'employees')
    contracts_directory = os.path.join(datadir, 'contracts')
    conttractsdocs = []
    for iroot, idirs, ifiles in os.walk(contracts_directory):
        if iroot == contracts_directory:
            print('Scanning %s for contracts' % iroot)
            for invf in ifiles:
                if re.search(pat, invf):
                    fullpath = os.path.join(iroot, invf)
                    invdoc = ET.parse(fullpath).getroot()
                    conttractsdocs.append(invdoc)
    print('%s contracts found' % len(conttractsdocs))
    for root, dirs, files in os.walk(employees_directory):
        if root == employees_directory:
            for f in files:
                if re.search(pat, f):
                    fullpath = os.path.join(root, f)
                    doc = ET.parse(fullpath).getroot()
                    print(
                        'Assembling employee "%s %s"' % (
                        doc.findall('firstname')[0].text, doc.findall('lastname')[0].text))

                    contracts_subele = doc.findall('contracts')
                    doc.remove(contracts_subele[0])
                    employee_id = doc.findall('id')[0].text
                    attach_contracts = []
                    for inv in conttractsdocs:
                        con_employee_id = inv.findall('employee_id')[0].text
                        if employee_id == con_employee_id:
                            attach_contracts.append(inv)
                    print('%s contracts found to add' % len(attach_contracts))
                    cdoc = doc_attach_collected_contracts(attach_contracts)
                    doc.append(cdoc)

                with open(fullpath, 'w') as fh:
                    fh.write(ET.tostring(doc))
                print('wrote %s' % fullpath)


def cached_clients_collect_contracts(datadir):
    contracts_directory = os.path.join(datadir, 'contracts')
    clients_directory = os.path.join(datadir, 'clients')
    conttractsdocs = []
    for iroot, idirs, ifiles in os.walk(contracts_directory):
        if iroot == contracts_directory:
            print('Scanning %s for contracts' % iroot)
            for invf in ifiles:
                if re.search(pat, invf):
                    fullpath = os.path.join(iroot, invf)
                    invdoc = ET.parse(fullpath).getroot()
                    conttractsdocs.append(invdoc)
    print('%s contracts found' % len(conttractsdocs))
    # loop through clients, update contracts subdoc
    for root, dirs, files in os.walk(clients_directory):
        if root == clients_directory:
            for f in files:
                if re.search(pat, f):
                    fullpath = os.path.join(root, f)
                    doc = ET.parse(fullpath).getroot()
                    print('Assembling client "%s"' % doc.findall('name')[0].text)
                    contracts_subele = doc.findall('contracts')
                    doc.remove(contracts_subele[0])
                    client_id = doc.findall('id')[0].text
                    attach_contracts = []
                    for inv in conttractsdocs:
                        con_client_id = inv.findall('client_id')[0].text
                        if client_id == con_client_id:
                            attach_contracts.append(inv)
                    print('%s contracts found to add' % len(attach_contracts))
                    cdoc = doc_attach_collected_contracts(attach_contracts)
                    doc.append(cdoc)
                with open(fullpath, 'w') as fh:
                    fh.write(ET.tostring(doc))
                print('wrote %s' % fullpath)


def cached_contracts_collect_invoices_and_items(datadir):
    invoices_directory = os.path.join(datadir, 'transactions', 'invoices')
    contract_items_directory = os.path.join(datadir, 'contracts', 'contract_items')
    contracts_directory = os.path.join(datadir, 'contracts')
    invdocs = []
    for iroot, idirs, ifiles in os.walk(invoices_directory):
        if iroot == invoices_directory:
            print('Scanning %s for invoices' % iroot)
            for invf in ifiles:
                if re.search(pat, invf):
                    fullpath = os.path.join(iroot, invf)
                    invdoc = ET.parse(fullpath).getroot()
                    invdocs.append(invdoc)
    print('%s invoices found' % len(invdocs))
    citemsdocs = []
    for iroot, idirs, ifiles in os.walk(contract_items_directory):
        if iroot == contract_items_directory:
            print('Scanning %s for contract items' % iroot)
            for invf in ifiles:
                if re.search(pat, invf):
                    fullpath = os.path.join(iroot, invf)
                    citemdoc = ET.parse(fullpath).getroot()
                    citemsdocs.append(citemdoc)
    print('%s contract items found' % len(citemsdocs))
    for root, dirs, files in os.walk(contracts_directory):
        if root == contracts_directory:
            for f in files:
                if re.search(pat, f):
                    fullpath = os.path.join(root, f)
                    doc = ET.parse(fullpath).getroot()
                    print('Assembling contract "%s"' % doc.findall('title')[0].text)

                    citem_subele = doc.findall('contract-items')
                    doc.remove(citem_subele[0])
                    inv_subele = doc.findall('invoices')
                    doc.remove(inv_subele[0])

                    contract_id = doc.findall('id')[0].text
                    attach_invs = []
                    for inv in invdocs:
                        inv_contract_id = inv.findall('contract_id')[0].text
                        if contract_id == inv_contract_id:
                            attach_invs.append(inv)
                    print('%s invoices found to add' % len(attach_invs))
                    cdoc = contract_attach_collected_invoices(attach_invs)
                    doc.append(cdoc)
                    attach_items = []
                    for citem in citemsdocs:
                        citem_contract_id = citem.findall('contract_id')[0].text
                        if contract_id == citem_contract_id:
                            attach_items.append(citem)
                    print('%s contract items to add' % len(attach_items))
                    cdoc = contract_attach_collected_contract_items(attach_items)
                    doc.append(cdoc)

                with open(fullpath, 'w') as fh:
                    fh.write(ET.tostring(doc))
                print('wrote %s' % fullpath)


def cache_obj(obj, full_path):
    if not os.path.isdir(os.path.dirname(full_path)):
        os.makedirs(os.path.dirname(full_path))
    with open(full_path, 'w') as fh:
        fh.write(ET.tostring(obj.to_xml()))
    obj.last_sync_time = dt.now()
    print('%s written' % full_path)


def cache_objs(datadir, objs):
    for obj in objs:

        full_path = full_non_dated_xml_obj_path(obj_dir(datadir, obj), obj)
        if os.path.isfile(full_path):
            if obj.last_sync_time is None or obj.modified_date is None:
                cache_obj(obj, full_path)
            elif obj.modified_date > obj.last_sync_time:
                cache_obj(obj, full_path)
        else:
            cache_obj(obj, full_path)
