import os
import re
import time
from datetime import datetime as dt
from xml.etree import ElementTree

from sqlalchemy.orm import sessionmaker

from s3_mysql_backup import TIMESTAMP_FORMAT
from s3_mysql_backup import DIR_CREATE_TIME_FORMAT
from s3_mysql_backup import mkdirs

from rrg.models import engine
from rrg.models import Employee
from rrg.models import Citem
from rrg.models import CommPayment

Session = sessionmaker(bind=engine)

session = Session()


def sherees_commissions_transactions_year_month(data_dir, year, month):

    return sherees_comm_payments_year_month(year, month), \
        sherees_comm_items_year_month(data_dir, year, month)


def sherees_comm_items_year_month(data_dir, y, m):
    xml_comm_items = []
    dir = sherees_comm_path_year_month(data_dir, y, str(m).zfill(2))
    for dirName, subdirList, fileList in os.walk(dir, topdown=False):
       
        for fname in fileList:
            filename = os.path.join(dir, dirName, fname)
            if re.search('transactions/invoices/invoice_items/commissions_items/[0-9]{4}/[0-9]{4}/[0-9]{0,1}[0-9]{0,1}/[0-9]{5}\.xml$', filename):
                xml_comm_items.append(Citem.from_xml(filename))

    return xml_comm_items


def sherees_comm_payments_year_month(y, m):
    if m < 12:
        nexty = y
        nextm = m + 1
    else:
        nexty = int(y) + 1
        nextm = 1

    return session.query(CommPayment)\
        .filter(CommPayment.employee==sa_sheree())\
        .filter(CommPayment.date >= '%s-%s-01' % (y, m))\
        .filter(CommPayment.date < '%s-%s-01' % (nexty, nextm))\
        .order_by(CommPayment.date)


def sa_sheree():
    """
    return sheree's sa object
    """
    return session.query(Employee).filter_by(firstname='sheree', salesforce=True)[0]


start = dt(year=2009, month=6, day=1)
end = dt(year=2016, month=1, day=1)


def comm_months(start=start, end=end):
    """
    returns dict of year/months between dates for comm report queries
    """
    date = start

    year_months = []
    while date < end:
        
        y = date.year
        m = date.month
        year_months.append({'year': y, 'month': m})
        if m < 12:
            m = m + 1
        else:
            m = 1
            y = y + 1
        
        date = dt(year=y, month=m, day=1)
        
    return year_months


def sherees_comm_path_year_month(data_dir, year, month):
    sheree = sa_sheree()    
    return os.path.join(data_dir, str(sheree.id), str(year), str(month))


def full_comm_item_xml_path(data_dir, comm_item):
    rel_dir = os.path.join(str(comm_item.employee_id), str(comm_item.date.year), str(comm_item.date.month).zfill(2))
    return os.path.join(data_dir, rel_dir, '%s.xml' % str(comm_item.id).zfill(5)), rel_dir


def directory_date_dictionary(data_dir):
    """
    returns dictionary of a directory in [{name: creation_date}] format
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
    """
    collect list comm items not on list
    """

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


def verify_comm_dirs_ready(data_dir, rel_dir_set):
    """
    run through the list of commissions directories created by db_data_dictionary_comm_item()
    """
    for d in rel_dir_set:
        dest = os.path.join(data_dir, d)
        mkdirs(dest)

def cache_comm_items(data_dir):

    disk_dict = directory_date_dictionary(data_dir)

    # Make query, assemble lists
    date_dict, citems, rel_dir_set = db_date_dictionary_comm_item(data_dir)

    #
    # Make sure destination directories exist
    #
    verify_comm_dirs_ready(data_dir, rel_dir_set)

    to_sync = []
    for comm_item in citems:
        file = full_comm_item_xml_path(data_dir, comm_item)
        # add to sync list if comm item not on disk
        if file[0] not in disk_dict:
            to_sync.append(comm_item)
        else:
            # check the rest of the business rules for syncing
            # no time stamps, timestamps out of sync
            if comm_item.last_sync_time is None or comm_item.modified_date is None:
                to_sync.append(comm_item)
                continue
            if comm_item.modified_date > comm_item.last_sync_time:
                to_sync.append(comm_item)

    # Write out xml
    for comm_item in to_sync:
        sync_comm_item(data_dir, comm_item)


def comm_item_xml_to_dict(citem):
    """
    returns dictionary from xml comm doc root
    generated from from_xml(xml_file_name)
    this function does not work in models??? date is casted as a VisitableType from SQLAlchemy
    """
    date_str =  citem.findall('date')[0].text
    return {
       'id': citem.findall('id')[0].text,
       'date': dt.strptime(date_str, TIMESTAMP_FORMAT),
       'description': citem.findall('description')[0].text,
       'amount': round(float(citem.findall('amount')[0].text)),
       'employee_id': citem.findall('employee_id')[0].text,
       'voided': int(citem.findall('voided')[0].text)
     }

def comm_item_xml_to_sa(citem):
    ci_dict = comm_item_xml_to_dict(citem)
    return Citem(id=ci_dict['id'], date=ci_dict['date'], description=ci_dict['description'], amount=ci_dict['amount'], employee_id=ci_dict['employee_id'], voided=ci_dict['voided'])