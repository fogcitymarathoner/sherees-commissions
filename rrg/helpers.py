import os
from datetime import datetime as dt
import xml.etree.ElementTree as ET

from s3_mysql_backup import TIMESTAMP_FORMAT
from s3_mysql_backup import MDY_FORMAT

class MissingEnvVar(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def date_to_datetime(date):
    return dt(year=date.year, month=date.month, day=date.day)


def read_inv_xml_file(xmlpath):
    if os.path.isfile(xmlpath):
        itree = ET.parse(xmlpath)
        iroot = itree.getroot()
        date = iroot.findall('date')[0].text
        amount = iroot.findall('amount')[0].text
        employee = iroot.findall('employee')[0].text
        voided = iroot.findall('voided')[0].text
    else:

        date = ''
        amount = ''
        employee = ''
        voided = '1'
        print('file %s is missing' % xmlpath)
    return date, amount, employee, voided


def xml_timestamp_to_mdy(ele, datetag):
    return dt.strptime(ele.findall(datetag)[0].text, TIMESTAMP_FORMAT).strftime(MDY_FORMAT)


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


def emp_memo_xml_doc_to_dict(ele):
    return {
        'id': ele.findall('id')[0].text,
        'date': xml_timestamp_to_mdy(ele, 'date'),
        'notes': ele.findall('notes')[0].text}


def emp_contract_xml_doc_to_dict(ele):
    return {
        'id': ele.findall('id')[0].text,
        'title': ele.findall('title')[0].text}


def emp_payment_xml_doc_to_dict(doc):
    return {
        'id': doc.findall('id')[0].text,
        'date': xml_timestamp_to_mdy(doc, 'date'),
        'check_number': doc.findall('ref')[0].text,
        'amount': doc.findall('amount')[0].text,
        'invoice_id': doc.findall('invoice_id')[0].text, }
