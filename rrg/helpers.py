import os
from datetime import datetime as dt
import xml.etree.ElementTree as ET

from s3_mysql_backup import TIMESTAMP_FORMAT
from s3_mysql_backup import YMD_FORMAT

class MissingEnvVar(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def read_inv_xml_file(xmlpath):
    if os.path.isfile(xmlpath):
        itree = ET.parse(xmlpath)
        iroot = itree.getroot()
        date = dt.strftime(dt.strptime(iroot.findall('date')[0].text, TIMESTAMP_FORMAT), YMD_FORMAT)
        amount = iroot.findall('amount')[0].text
        employee = iroot.findall('employee')[0].text
        contract_id_ele = iroot.findall('contract_id')[0]
        client = contract_id_ele.attrib['client']
        voided = iroot.findall('voided')[0].text
        terms = iroot.findall('terms')[0].text
        sqlid = int(iroot.findall('id')[0].text)
    else:

        date = ''
        amount = ''
        employee = ''
        voided = '1'
        terms = ''
        sqlid = ''
        client = ''
        print('file %s is missing' % xmlpath)
    return date, amount, employee, voided, terms, sqlid, client

