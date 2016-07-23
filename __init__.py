
import os
import time
from datetime import datetime as dt

from s3_mysql_backup import DIR_CREATE_TIME_FORMAT

from sqlalchemy.orm import sessionmaker
from models import engine
from models import Citem


def directory_date_dictionary(data_dir):
    """
    returns dictionary of a directory in (name: cdate} format
    :param data_dir:
    :return:
    """
    dirFileList = []
    for dirName, subdirList, fileList in os.walk(data_dir, topdown=False):
        if data_dir == dirName:
            for f in fileList:

                dirFileList.append(os.path.join(dirName, f))

    return {f: dt.strptime(time.ctime(os.path.getmtime(f)), DIR_CREATE_TIME_FORMAT) for f in dirFileList}


def db_date_dictionary_comm_item(data_dir):
    """
    returns database dictionary counter part to dicectory_date_dictionary for sync determination
    :param data_dir:
    :return:
    """
    Session = sessionmaker(bind=engine)

    session = Session()

    citem_dict = {}

    for comm_item in session.query(Citem).order_by(Citem.id):
        f = os.path.join(data_dir, '%s.xml' % str(comm_item.id).zfill(5))
        citem_dict[f] = comm_item.last_sync_time

    return citem_dict


def get_list_of_comm_items_to_sync(data_dir):

    disk_dict = directory_date_dictionary(data_dir)
    db_dict = db_date_dictionary_comm_item(data_dir)

    sync_list = []
    for ci in db_dict:
        if ci not in disk_dict:
            sync_list.append(int(os.path.basename(ci)).split('.')[1])

    return sync_list

print(get_list_of_comm_items_to_sync('/php-apps/cake.rocketsredglare.com/rrg/data/transactions/invoices/invoice_items/commissions_items/'))