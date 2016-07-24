
import os
import time
from datetime import datetime as dt
from xml.etree import ElementTree
from s3_mysql_backup import mkdirs
from s3_mysql_backup import DIR_CREATE_TIME_FORMAT

from sqlalchemy.orm import sessionmaker
from models import engine
from models import Citem


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

data_dir = '/php-apps/cake.rocketsredglare.com/rrg/data/transactions/invoices/invoice_items/commissions_items/'
# orphen_citems = get_comm_items_without_parents(data_dir)
# delete_orphen_comm_items(orphen_citems)

date_dict, citems, rel_dir_set = db_date_dictionary_comm_item(data_dir)
#
# make directories in advance
for d in rel_dir_set:
    mkdirs(os.path.join(data_dir, d), writeable=True)

disk_dict = directory_date_dictionary(data_dir)

for comm_item in citems:

    sync_comm_item(data_dir, comm_item)
    # print(comm_item)
    # f, rel_dir = full_comm_item_xml_path(data_dir, comm_item)
    # if f not in disk_dict:
    #     sync_comm_item(data_dir, comm_item)
    # else:
    #     # correct Null modified dates
    #     if comm_item.modified_date is None:
    #
    #         session.query(Citem).filter_by(id=comm_item.id).update({"modified_date": dt.now()})
    #
    #         session.commit()
    #         comm_item.modified_date = dt.now()
    #
    #     if comm_item.last_sync_time is None:
    #
    #         sync_comm_item(data_dir, comm_item)
    #
    #     elif comm_item.modified_date > comm_item.last_sync_time:
    #
    #         sync_comm_item(data_dir, comm_item)
    #     else:
    #         print('%s already synced' % comm_item)
session.commit()
session.close()

"""
print(get_list_of_comm_items_to_sync('/php-apps/cake.rocketsredglare.com/rrg/data/transactions/invoices/invoice_items/commissions_items/'))


<?xml version="1.0"?>
<invoices-items-commissions-item>
  <id>6431</id>
  <employee_id>1479</employee_id>
  <invoices_item_id>4298</invoices_item_id>
  <invoice_id>3356</invoice_id>
  <commissions_report_id>3356</commissions_report_id>
  <commissions_reports_tag_id>361</commissions_reports_tag_id>
  <description>xxx dddd - Overtime</description>
  <date>2012-08-12</date>
  <percent>38.5</percent>
  <amount>22.45</amount>
  <rel_inv_amt>1788.9</rel_inv_amt>
  <rel_inv_line_item_amt>249.895</rel_inv_line_item_amt>
  <rel_item_amt>57.7125</rel_item_amt>
  <rel_item_quantity>4.33</rel_item_quantity>
  <rel_item_cost>42.75</rel_item_cost>
  <rel_item_amt>57.7125</rel_item_amt>
  <cleared>1</cleared>
  <voided>0</voided>
  <date_generated>Mon, 11 Jul 2016 11:19:59</date_generated>
</invoices-items-commissions-item>
"""
