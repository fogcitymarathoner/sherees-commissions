import os
import re
from datetime import datetime as dt
from tabulate import tabulate
import xml.etree.ElementTree as ET
import logging

from s3_mysql_backup import TIMESTAMP_FORMAT
from s3_mysql_backup import YMD_FORMAT

logging.basicConfig(filename='testing.log', level=logging.DEBUG)
logger = logging.getLogger('test')

logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

pat = '[0-9]{5}\.[xX][Mm][Ll]$'


def date_to_datetime(date):
    return dt(year=date.year, month=date.month, day=date.day)


def xml_timestamp_to_mdy(ele, datetag):
    return dt.strptime(ele.findall(datetag)[0].text, TIMESTAMP_FORMAT).strftime(YMD_FORMAT)


def emp_payment_xml_doc_to_dict(doc):
    return {
        'id': doc.findall('id')[0].text,
        'date': xml_timestamp_to_mdy(doc, 'date'),
        'check_number': doc.findall('ref')[0].text,
        'amount': doc.findall('amount')[0].text,
        'invoice_id': doc.findall('invoice_id')[0].text, }


def emp_memo_xml_doc_to_dict(ele):
    return {
        'id': ele.findall('id')[0].text,
        'date': xml_timestamp_to_mdy(ele, 'date'),
        'notes': ele.findall('notes')[0].text}


def emp_contract_xml_doc_to_dict(ele):
    return {
        'id': ele.findall('id')[0].text,
        'title': ele.findall('title')[0].text}


def emp_xml_doc_to_dict(i, doc, emp_dict):
    emp_dict['index'] = i
    emp_dict['id'] = doc.findall('id')[0].text
    emp_dict['firstname'] = doc.findall('firstname')[0].text
    emp_dict['lastname'] = doc.findall('lastname')[0].text
    emp_dict['street1'] = doc.findall('street1')[0].text
    emp_dict['street2'] = doc.findall('street2')[0].text
    emp_dict['city'] = doc.findall('city')[0].text
    emp_dict['state'] = doc.findall('state')[0].text
    emp_dict['zip'] = doc.findall('zip')[0].text
    emp_dict['startdate'] = xml_timestamp_to_mdy(doc, 'startdate')
    emp_dict['enddate'] = xml_timestamp_to_mdy(doc, 'enddate')
    emp_dict['dob'] = xml_timestamp_to_mdy(doc, 'dob')
    emp_dict['salesforce'] = doc.findall('salesforce')[0].text
    return emp_dict


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

                    if i == int(id):
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

