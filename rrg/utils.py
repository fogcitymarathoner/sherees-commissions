import os
import time
from datetime import datetime as dt
from sqlalchemy import create_engine
from rrg.archive import employee_dated_object_reldir
from rrg.archive import obj_dir
from rrg.archive import full_non_dated_xml_obj_path
from rrg.models import Base

from s3_mysql_backup import DIR_CREATE_TIME_FORMAT

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
        engine = create_engine('mysql+mysqldb://%s:%s@%s:%s/%s' % (args.db_user, args.db_pass, args.mysql_host,
                                                                   args.mysql_port, args.db))

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


def commissions_item_dir(datadir, comm_item):
    return full_non_dated_xml_obj_path(datadir, comm_item)


def commissions_payment_dir(datadir, comm_payment):
    return obj_dir(datadir, comm_payment) + employee_dated_object_reldir(comm_payment)

