import os
import re
import time
from datetime import datetime as dt

from s3_mysql_backup import DIR_CREATE_TIME_FORMAT
from s3_mysql_backup import mkdirs
from s3_mysql_backup import s3_bucket

from sqlalchemy import create_engine

from rrg.lib import archive

monthy_statement_ym_header = '%s/%s - #########################################################'


class Args(object):
    mysql_host = 'localhost'
    mysql_port = 3306
    db_user = 'root'
    db_pass = 'my_very_secret_password'
    db = 'rrg_test'


def create_db():
    """
    this routine has a bug, DATABASE isn't fully integrated right, the line
    DATABASE = 'rrg' in rrg/__init__.py has to be temporarily hardcoded to
    'rrg_test' or whatever
    :return:
    """
    args = Args()
    if args.mysql_host == 'localhost':
        engine = create_engine(
            'mysql+mysqldb://%s:%s@%s:%s/%s' % (args.db_user, args.db_pass, args.mysql_host, args.mysql_port, args.db))

        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
    else:
        print('This routine only builds test databases on localhost')


def directory_date_dictionary(data_dir):
    """
    returns dictionary of a directory in [{name: creation_date}] format
    :rtype: object
    :param data_dir:
    :return:
    """
    dirFileList = []
    for dirName, subdirList, fileList in os.walk(data_dir, topdown=True):
        for f in fileList:
            dirFileList.append(os.path.join(dirName, f))

    return {
        f: dt.strptime(time.ctime(os.path.getmtime(f)), DIR_CREATE_TIME_FORMAT)
        for
        f in dirFileList}


def transactions_invoice_items_dir(datadir):
    return os.path.join(os.path.join(datadir, 'transactions', 'invoices'), 'invoice_items')


def transactions_invoice_payments_dir(datadir):
    return os.path.join(os.path.join(datadir, 'transactions', 'invoices'), 'invoice_payments')


def clients_open_invoices_dir(datadir):
    return os.path.join(os.path.join(datadir, 'clients'), 'open_invoices')


def clients_statements_dir(datadir):
    return os.path.join(os.path.join(datadir, 'clients'), 'statements')


def clients_ar_xml_file(datadir):
    return os.path.join(os.path.join(datadir, 'transactions', 'invoices'), 'ar.xml')


def clients_managers_dir(datadir):
    return os.path.join(os.path.join(datadir, 'clients'), 'managers')


def commissions_item_reldir(comm_item):
    return archive.employee_dated_object_reldir(comm_item)[1:len(archive.employee_dated_object_reldir(comm_item))]


def commissions_item_fullpathname(datadir, comm_item):
    xfilename = os.path.join('%s.xml' % str(comm_item.id).zfill(5))

    return os.path.join(
        datadir,
        'transactions', 'invoices', 'invoice_items', 'commissions_items', commissions_item_reldir(comm_item), xfilename)


def commissions_payment_dir(datadir, comm_payment):
    return archive.obj_dir(datadir, comm_payment) + archive.employee_dated_object_reldir(comm_payment)


def employees_memos_dir(datadir):
    return os.path.join(datadir, 'employees', 'memos')


def download_last_database_backup(aws_access_key_id, aws_secret_access_key, bucket_name, project_name, db_backups_dir):

    archive_file_extension = 'sql.bz2'
    if os.name == 'nt':
        raise NotImplementedError

    else:
        bucket = s3_bucket(aws_access_key_id, aws_secret_access_key, bucket_name)

        bucketlist = bucket.list()

        TARFILEPATTERN = "[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]-[0-9][0-9]-[0-9][0-9]-[0-9][0-9]-%s.%s" % \
                         (project_name, archive_file_extension)

        #
        # delete files over a month old, locally and on server
        #
        backup_list = []
        for f in bucketlist:
            parray = f.name.split('/')
            filename = parray[len(parray)-1]
            if re.match(TARFILEPATTERN, filename):
                farray = f.name.split('/')
                fname = farray[len(farray)-1]
                dstr = fname[0:19]

                fdate = dt.strptime(dstr, "%Y-%m-%d-%H-%M-%S")
                backup_list.append({'date': fdate, 'key': f})

        backup_list = sorted(
            backup_list, key=lambda k: k['date'], reverse=True)

        if len(backup_list) > 0:
            last_backup = backup_list[0]
            keyString = str(last_backup['key'].key)
            basename = os.path.basename(keyString)
            # check if file exists locally, if not: download it

            mkdirs(db_backups_dir)

            dest = os.path.join(db_backups_dir, basename)
            print('Downloading %s to %s' % (keyString, dest))
            if not os.path.exists(dest):
                with open(dest, 'wb') as f:
                    last_backup['key'].get_contents_to_file(f)
            return last_backup['key']
        else:
            print('There is no S3 backup history for project %s' % project_name)
            print('In ANY Folder of bucket %s' % bucket_name)

import os
import re
from datetime import datetime as dt
from tabulate import tabulate
import xml.etree.ElementTree as ET
import logging

from rrg.lib import archive
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
    """
    attaches contracts with transactions to clients docs for archiving
    :param datadir:
    :return:
    """
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
    clients_memos_directory = os.path.join(datadir, 'clients', 'memos')
    memossdocs = []
    for iroot, idirs, ifiles in os.walk(contracts_directory):
        if iroot == contracts_directory:
            print('Scanning %s for memos' % iroot)
            for invf in ifiles:
                if re.search(pat, invf):
                    fullpath = os.path.join(iroot, invf)
                    memodoc = ET.parse(fullpath).getroot()
                    memossdocs.append(memodoc)
    print('%s memos found' % len(memossdocs))
    clients_managers_directory = os.path.join(datadir, 'clients', 'managers')
    managersdocs = []
    for iroot, idirs, ifiles in os.walk(clients_managers_directory):
        if iroot == clients_managers_directory:
            print('Scanning %s for memos' % iroot)
            for invf in ifiles:
                if re.search(pat, invf):
                    fullpath = os.path.join(iroot, invf)
                    memodoc = ET.parse(fullpath).getroot()
                    managersdocs.append(memodoc)
    print('%s managers found' % len(managersdocs))
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
    """
    appends transactions to contracts
    :param datadir:
    :return:
    """
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

        full_path = full_non_dated_xml_obj_path(archive.obj_dir(datadir, obj), obj)
        if os.path.isfile(full_path):
            if obj.last_sync_time is None or obj.modified_date is None:
                cache_obj(obj, full_path)
            elif obj.modified_date > obj.last_sync_time:
                cache_obj(obj, full_path)
        else:
            cache_obj(obj, full_path)
