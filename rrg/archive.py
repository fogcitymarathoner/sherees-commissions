import os
import re
from tabulate import tabulate
import xml.etree.ElementTree as ET


pat = '[0-9]{5}\.[xX][Mm][Ll]$'


def employees(args):
    ids = []
    firsts = []
    lasts = []
    i = 1
    for root, dirs, files in os.walk(args.datadir):
        if root == args.datadir:
            print('root="%s"' % root)
            for f in files:
                if re.search(pat, f):
                    fullpath = os.path.join(root, f)
                    doc = ET.parse(fullpath).getroot()
                    firstname = doc.findall('firstname')[0].text
                    lastname = doc.findall('lastname')[0].text
                    ids.append(str(i))
                    firsts.append(firstname)
                    lasts.append(lastname)
                    i += 1
    res_dict_transposed = {
        'id': [i for i in ids],
        'first': [i for i in firsts],
        'last': [i for i in lasts],
    }
    print(tabulate(res_dict_transposed, headers='keys', tablefmt='plain'))


def employee(args):
    i = 1
    for root, dirs, files in os.walk(args.datadir):
        if root == args.datadir:
            print('root="%s"' % root)
            for f in files:

                if re.search(pat, f):
                    if i == args.id:
                        fullpath = os.path.join(root, f)
                        doc = ET.parse(fullpath).getroot()
                        firstname = doc.findall('firstname')[0].text
                        lastname = doc.findall('lastname')[0].text
                        print ('id="%s", first="%s", last="%s"' % (i, firstname, lastname))
                    i += 1


def employee_attach_collected_contracts(emp_doc, contract_doc_list):

    emp_contracts_doc = emp_doc.findall('contracts')[0]
    for condoc in contract_doc_list:
        emp_contracts_doc.append(condoc)
    return emp_doc


def contracts(args):
    ids = []
    titles = []
    clients = []
    employees = []
    i = 1
    for root, dirs, files in os.walk(args.datadir):
        if root == args.datadir:
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


def contract(args):
    i = 1
    for root, dirs, files in os.walk(args.datadir):
        if root == args.datadir:
            print('root="%s"' % root)
            for f in files:
                if re.search(pat, f):
                    if i == args.id:
                        fullpath = os.path.join(root, f)
                        doc = ET.parse(fullpath).getroot()
                        title = doc.findall('title')[0].text
                        client = doc.findall('client')[0].text
                        employee = doc.findall('employee')[0].text
                        print ('id="%s", title="%s", client="%s", employee="%s' % (i, title, client, employee))
                    i += 1


def client_attach_collected_contracts(cl_doc, contract_doc_list):

    cl_contracts_doc = cl_doc.findall('contracts')[0]
    for condoc in contract_doc_list:
        cl_contracts_doc.append(condoc)
    return cl_doc