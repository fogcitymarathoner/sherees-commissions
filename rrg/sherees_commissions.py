import os
import time
from datetime import datetime as dt
from xml.etree import ElementTree

from s3_mysql_backup import DIR_CREATE_TIME_FORMAT
from sqlalchemy.orm import sessionmaker

from rrg.models import engine

from rrg.models import Citem

Session = sessionmaker(bind=engine)

session = Session()


def full_comm_item_xml_path(data_dir, comm_item):
    rel_dir = os.path.join(str(comm_item.employee_id), str(comm_item.date.year), str(comm_item.date.month))
    return os.path.join(data_dir, rel_dir, '%s.xml' % str(comm_item.id).zfill(5)), rel_dir


def directory_date_dictionary(data_dir):
    """
    returns dictionary of a directory in (name: cdate} format
    :param data_dir:
    :return:
    """
    dirFileList = []
    for dirName, subdirList, fileList in os.walk(data_dir, topdown=True):
        for f in fileList:

            dirFileList.append(os.path.join(dirName, f))

    return {f: dt.strptime(time.ctime(os.path.getmtime(f)), DIR_CREATE_TIME_FORMAT) for f in dirFileList}


def db_date_dictionary_comm_item(data_dir):
    """
    returns database dictionary counter part to dicectory_date_dictionary for sync determination
    :param data_dir:
    :return:
    """

    citem_dict = {}
    rel_dir_set = set()
    citems = session.query(Citem).order_by(Citem.id)

    for comm_item in citems:
        f, rel_dir = full_comm_item_xml_path(data_dir, comm_item)
        rel_dir_set.add(rel_dir)
        citem_dict[f] = comm_item.last_sync_time

    return citem_dict, citems, rel_dir_set


def get_comm_items_without_parents(data_dir):
    citem_dict, citems, rel_dir_set = db_date_dictionary_comm_item(data_dir)
    orphens = []
    for comm_item in citems:
        if comm_item.invoices_item is None:
            orphens.append(comm_item)

    return orphens


def get_list_of_comm_items_to_sync(data_dir):

    disk_dict = directory_date_dictionary(data_dir)
    db_dict, citems, rel_dir_set  = db_date_dictionary_comm_item(data_dir)

    sync_list = []
    for ci in db_dict:
        if ci not in disk_dict:
            sync_list.append(int(os.path.basename(ci).split('.')[0]))

    return sync_list


def sync_comm_item(data_dir, comm_item):
    """
    writes xml file for commissions item
    """
    f, rel_dir = full_comm_item_xml_path(data_dir, comm_item)
    with open(f, 'w') as fh:
        fh.write(ElementTree.tostring(comm_item.to_xml()))

    # Fix bad modified_date
    if comm_item.modified_date is None:
        session.query(Citem).filter_by(id=comm_item.id).update({"modified_date": dt.now()})

    session.query(Citem).filter_by(id=comm_item.id).update({"last_sync_time": dt.now()})
    print('%s written' % f)


def delete_orphen_comm_items(comm_items):
    """
    deletes list of orphened comm_items identified by get_comm_items_without_parents
    """

    for ci in comm_items:
        session.delete(ci)
        print('deleted orphen invoice %s' % ci)

    session.commit()


def cache_comm_items(data_dir):

    disk_dict = directory_date_dictionary(data_dir)

    date_dict, citems, rel_dir_set = db_date_dictionary_comm_item(data_dir)
    #

    to_sync = []
    for comm_item in citems:
        file = full_comm_item_xml_path(data_dir, comm_item)
        if file[0] not in disk_dict:
            to_sync.append(comm_item)
        else:
            if comm_item.last_sync_time is None or comm_item.modified_date is None:
                to_sync.append(comm_item)
                continue
            if comm_item.modified_date > comm_item.last_sync_time:
                to_sync.append(comm_item)

    for comm_item in to_sync:

        sync_comm_item(data_dir, comm_item)

