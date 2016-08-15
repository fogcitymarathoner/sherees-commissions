import os
from datetime import datetime as dt
import xml.etree.ElementTree as ET


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

