import os
import re
from tabulate import tabulate
import xml.etree.ElementTree as ET
import logging


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


def doc_attach_collected_contracts(doc, contract_doc_list):
    et_search = doc.findall('contracts')
    if et_search:
        csub_ele = et_search[0]
        csub_ele.clear()

    else:
        csub_ele = ET.SubElement(doc, 'invoices')

    for condoc in contract_doc_list:
        _ = ET.SubElement(csub_ele, 'contract')
        _ = condoc

    return doc


def contract_attach_collected_invoices(contract_doc, inv_doc_list):
    """
    attached contracts invoicers list gathered from disk
    :param contract_doc:
    :param inv_doc_list:
    :return:
    """
    et_search = contract_doc.findall('invoices')
    if et_search:
        isub_ele = et_search[0]
        isub_ele.clear()
    else:
        isub_ele = ET.SubElement(contract_doc, 'invoices')

    for idoc in inv_doc_list:
        logger.debug(ET.tostring(idoc))
        isub_ele.append(idoc)

    return contract_doc


def contract_attach_collected_contract_items(contract_doc, citem_doc_list):
    """
    attached contracts invoicers list gathered from disk
    :param contract_doc:
    :param citem_doc_list:
    :return:
    """
    et_search = contract_doc.findall('contract-items')
    if et_search:
        isub_ele = et_search[0]
        isub_ele.clear()
    else:
        isub_ele = ET.SubElement(contract_doc, 'contract-items')

    for idoc in citem_doc_list:
        logger.debug(ET.tostring(idoc))
        isub_ele.append(idoc)

    return contract_doc


def cached_contracts_collect_invoices_and_items(args):

    invdocs = []
    for iroot, idirs, ifiles in os.walk(args.invoices_dir):
        if iroot == args.invoice_sdir:
            print('Scanning %s for invoices' % iroot)
            for invf in ifiles:
                if re.search(pat, invf):
                    fullpath = os.path.join(iroot, invf)
                    invdoc = ET.parse(fullpath).getroot()
                    invdocs.append(invdoc)
    print('%s invoices found' % len(invdocs))
    citemsdocs = []
    for iroot, idirs, ifiles in os.walk(args.contract_items_dir):
        if iroot == args.invoicesdir:
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
                    contract_subele = doc.findall('contracts/contract')
                    contract_id = contract_subele.findall('id')[0].text
                    attach_invs = []
                    for inv in invdocs:
                        inv_contract_id = inv.findall('contract_id')[0].text
                        if contract_id == inv_contract_id:
                            attach_invs.append(inv)
                    print('%s invoices found to add' % len(attach_invs))
                    cdoc = contract_attach_collected_invoices(contract_subele, attach_invs)
                    _ = ET.SubElement(contract_subele, 'invoices')
                    _ = cdoc
                    attach_items = []
                    for citem in citemsdocs:
                        citem_contract_id = citem.findall('contract_id')[0].text
                        if contract_id == citem_contract_id:
                            attach_items.append(citem)
                    print('%s contract items to add' % len(attach_items))
                    cdoc = contract_attach_collected_contract_items(contract_subele, invdocs)
                    _ = ET.SubElement(contract_subele, 'contract-items')
                    _ = cdoc

                with open(fullpath, 'w') as fh:
                    fh.write(ET.tostring(doc))
                print('wrote %s' % f)
