import os
import time
from datetime import datetime as dt
from sqlalchemy import create_engine
from rrg.models import Contract
from rrg.models import Base

from s3_mysql_backup import DIR_CREATE_TIME_FORMAT


monthy_statement_ym_header = '%s/%s - #########################################################'


def clear_out_bad_contracts():
    """
    removed contracts from the database that have either employee_id or
    client_id 0 or None
    """
    session.query(
        Contract).filter(
        Contract.employee_id == 0, Contract.client_id == 0).delete(
        synchronize_session=False)
    session.commit()


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


def transactions_invoices_dir(datadir):
    return os.path.join(datadir, 'transactions', 'invoices')


def transactions_invoice_items_dir(datadir):
    return os.path.join(transactions_invoices_dir(datadir), 'invoice_items')


def transactions_invoice_payments_dir(datadir):
    return os.path.join(transactions_invoices_dir(datadir), 'invoice_payments')


def clients_dir(datadir):
    return os.path.join(datadir, 'clients')


def clients_managers_dir(datadir):
    return os.path.join(clients_dir(datadir), 'managers')


def clients_checks_dir(datadir):
    return os.path.join(datadir, 'transactions', 'checks')


def clients_memos_dir(datadir):
    return os.path.join(clients_dir(datadir), 'memos')


def clients_open_invoices_dir(datadir):
    return os.path.join(clients_dir(datadir), 'open_invoices')


def clients_statements_dir(datadir):
    return os.path.join(clients_dir(datadir), 'statements')


def clients_ar_xml_file(datadir):
    return os.path.join(transactions_invoices_dir(datadir), 'ar.xml')


def employees_dir(datadir):
    return os.path.join(datadir, 'employees')


def employees_memos_dir(datadir):
    return os.path.join(datadir, 'employees', 'memos')


def employees_payments_dir(datadir):
    return os.path.join(datadir, 'employees', 'payments')


def contracts_dir(datadir):
    return os.path.join(datadir, 'contracts')


def contracts_items_dir(datadir):
    return os.path.join(datadir, 'contracts', 'contract_items')


def commissions_items_dir(datadir):
    return os.path.join(datadir, 'transactions', 'invoices', 'invoice_items', 'commissions_items')


def commissions_payments_dir(datadir):
    return os.path.join(datadir, 'transactions', 'invoices', 'invoice_items', 'commissions_payments')


def employee_dated_object_reldir(obj):
    return os.path.sep + os.path.join(str(obj.employee_id).zfill(5),
                                      str(obj.date.year),
                                      str(obj.date.month).zfill(2))


def commissions_item_dir(datadir, comm_item):
    return commissions_items_dir(datadir) + employee_dated_object_reldir(comm_item)


def commissions_payment_dir(datadir, comm_payment):
    return commissions_payments_dir(datadir) + employee_dated_object_reldir(comm_payment)
