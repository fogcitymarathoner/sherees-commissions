
import os
import time
from datetime import datetime as dt

from s3_mysql_backup import DIR_CREATE_TIME_FORMAT

from sqlalchemy.orm import sessionmaker
from models import engine
from models import Citem


def directory_date_dictionary(dir):
    """
    returns dictionary of a directory in (name: cdate} format
    :param dir:
    :return:
    """
    dirFileList = []
    for dirName, subdirList, fileList in os.walk(dir, topdown=False):
        if dir == dirName:
            for f in fileList:

                dirFileList.append(os.path.join(dirName, f))

    return {f: dt.strptime(time.ctime(os.path.getmtime(f)), DIR_CREATE_TIME_FORMAT) for f in dirFileList}


def db_date_dictionary_comm_item(dir):
    """
    returns database dictionary counter part to dicectory_date_dictionary for sync determination
    :param dir:
    :return:
    """
    Session = sessionmaker(bind=engine)

    session = Session()

    citem_dict = {}

    for comm_item in session.query(Citem).order_by(Citem.id):
        f = os.path.join(dir, '%s.xml' % str(comm_item.id).zfill(5))
        citem_dict[f] = comm_item.last_sync_time

    return citem_dict

