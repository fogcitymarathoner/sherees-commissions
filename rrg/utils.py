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
