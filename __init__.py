
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
            sync_list.append(int(os.path.basename(ci).split('.')[0]))

    return sync_list

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
