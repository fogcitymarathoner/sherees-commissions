import os
import re
from tabulate import tabulate
import xml.etree.ElementTree as ET
import logging

from rrg.billing import employee_payment_fullpath
from rrg.helpers import xml_timestamp_to_mdy
from rrg.helpers import emp_xml_doc_to_dict
from rrg.helpers import emp_memo_xml_doc_to_dict
from rrg.helpers import emp_contract_xml_doc_to_dict
from rrg.helpers import emp_payment_xml_doc_to_dict

logging.basicConfig(filename='testing.log', level=logging.DEBUG)
logger = logging.getLogger('test')

logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

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
        'dob': None,
        'contracts': [],
        'memos': [],
        'payments': [],
    }
    for root, dirs, files in os.walk(args.datadir):
        if root == args.datadir:
            for f in files:
                if re.search(pat, f):
                    if i == args.id:
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
                                _ = employee_payment_fullpath(args.datadir, ele[0].text)
                                doc = ET.parse(_).getroot()
                                emp_dict['payments'].append(emp_payment_xml_doc_to_dict(doc))
                        break
                    i += 1
    return emp_dict


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


def cached_employees_collect_contracts(args):
    conttractsdocs = []
    for iroot, idirs, ifiles in os.walk(args.contracts_dir):
        if iroot == args.contracts_dir:
            print('Scanning %s for contracts' % iroot)
            for invf in ifiles:
                if re.search(pat, invf):
                    fullpath = os.path.join(iroot, invf)
                    invdoc = ET.parse(fullpath).getroot()
                    conttractsdocs.append(invdoc)
    print('%s contracts found' % len(conttractsdocs))

    for root, dirs, files in os.walk(args.datadir):
        if root == args.datadir:
            for f in files:
                if re.search(pat, f):
                    fullpath = os.path.join(root, f)
                    doc = ET.parse(fullpath).getroot()
                    print(
                    'Assembling employee "%s %s"' % (doc.findall('firstname')[0].text, doc.findall('lastname')[0].text))

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


def cached_clients_collect_contracts(args):
    conttractsdocs = []
    for iroot, idirs, ifiles in os.walk(args.contracts_dir):
        if iroot == args.contracts_dir:
            print('Scanning %s for contracts' % iroot)
            for invf in ifiles:
                if re.search(pat, invf):
                    fullpath = os.path.join(iroot, invf)
                    invdoc = ET.parse(fullpath).getroot()
                    conttractsdocs.append(invdoc)
    print('%s contracts found' % len(conttractsdocs))

    # loop through clients, update contracts subdoc
    for root, dirs, files in os.walk(args.datadir):
        if root == args.datadir:
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


def cached_contracts_collect_invoices_and_items(args):
    invdocs = []
    for iroot, idirs, ifiles in os.walk(args.invoices_dir):
        if iroot == args.invoices_dir:
            print('Scanning %s for invoices' % iroot)
            for invf in ifiles:
                if re.search(pat, invf):
                    fullpath = os.path.join(iroot, invf)
                    invdoc = ET.parse(fullpath).getroot()
                    invdocs.append(invdoc)
    print('%s invoices found' % len(invdocs))
    citemsdocs = []
    for iroot, idirs, ifiles in os.walk(args.contract_items_dir):
        if iroot == args.contract_items_dir:
            print('Scanning %s for contract items' % iroot)
            for invf in ifiles:
                if re.search(pat, invf):
                    fullpath = os.path.join(iroot, invf)
                    citemdoc = ET.parse(fullpath).getroot()
                    citemsdocs.append(citemdoc)
    print('%s contract items found' % len(citemsdocs))
    for root, dirs, files in os.walk(args.datadir):
        if root == args.datadir:
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
