
import os
import re
import time
from datetime import datetime as dt

from subprocess import call
import random
import string

import xml.etree.ElementTree as ET
import xml.dom.minidom as xml_pp

from sqlalchemy import create_engine
from rrg.employees import employees as sa_employees
from rrg.employees import picked_employee
from rrg.models import Employee
from rrg.archive import employee_dated_object_reldir
from rrg.archive import obj_dir
from rrg.models import Base
from rrg.invoices import open_invoices as sa_open_invoices
from rrg.timecards import  timecards as sa_timecards
from rrg.timecards import picked_timecard
from rrg.invoices import picked_open_invoice
from rrg.models import Invoice
from rrg.models import Iitem

from s3_mysql_backup import DIR_CREATE_TIME_FORMAT
from s3_mysql_backup import s3_bucket
from s3_mysql_backup import mkdirs


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
    return employee_dated_object_reldir(comm_item)[1:len(employee_dated_object_reldir(comm_item))]


def commissions_item_fullpathname(datadir, comm_item):
    xfilename = os.path.join('%s.xml' % str(comm_item.id).zfill(5))

    return os.path.join(
        datadir,
        'transactions', 'invoices', 'invoice_items', 'commissions_items', commissions_item_reldir(comm_item), xfilename)


def commissions_payment_dir(datadir, comm_payment):
    return obj_dir(datadir, comm_payment) + employee_dated_object_reldir(comm_payment)


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
            print 'There is no S3 backup history for project %s' % project_name
            print 'In ANY Folder of bucket %s' % bucket_name


def edit_employee(session, crypter, number):
    w_employees = sa_employees(session)

    if number in range(1, w_employees.count() + 1):

        employee = picked_employee(session, number)
        xml = xml_pp.parseString(ET.tostring(employee.to_xml(crypter)))
        temp_file = os.path.join(
            os.path.sep, 'tmp', ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(40)))
        with open(temp_file, 'w+b') as f:
            f.write(xml.toprettyxml())
        call(["vi", temp_file])
        whole_emp_xml = Employee.from_xml(temp_file)

        employee.update_from_xml_doc(whole_emp_xml, crypter)

        session.commit()
    else:
        print('Employee number is not in range')
        quit()


def edit_invoice(session, crypter, phase, number):

    if phase == 'open':
        winvoices = sa_open_invoices(session)
    elif phase =='timecard':
        winvoices = sa_timecards(session)
    if number in xrange(1, winvoices.count() + 1):
        if phase == 'open':
            invoice = picked_open_invoice(session, number)
        elif phase =='timecard':
            invoice = picked_timecard(session, number)
        xml = xml_pp.parseString(ET.tostring(invoice.to_xml(crypter)))
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
