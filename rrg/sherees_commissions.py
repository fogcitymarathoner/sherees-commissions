import os
import xml.etree.ElementTree as ET
from datetime import datetime as dt
from datetime import timedelta as td
from xml.dom import minidom

from s3_mysql_backup import mkdirs
from sqlalchemy import and_

from rrg.billing import verify_dirs_ready
from rrg.commissions import comm_months
from rrg.commissions import employee_commissions_transactions_year_month
from rrg.commissions import iitem_exclude
from rrg.commissions import sales_person_invoices_of_interest
from rrg.lib import archive
from rrg.models import Citem
from rrg.models import Employee
from rrg.models import Invoice
from rrg.utils import commissions_item_fullpathname
from rrg.utils import commissions_item_reldir
from rrg.utils import directory_date_dictionary


def sa_sheree(session):
    """
    return sheree's sa object
    """
    return \
        session.query(Employee).filter_by(firstname='sheree', salesforce=True)[0]


def db_date_dictionary_comm_item(session, datadir):
    """
    returns database dictionary counter part to directory_date_dictionary for sync determination
    :param data_dir: assumes 'transactions/invoices/.../comm_items' prepended
    :return:
    """
    citem_dict = {}
    rel_dir_set = set()
    citems = session.query(Citem).order_by(Citem.id)
    for comm_item in citems:
        f = commissions_item_fullpathname(datadir, comm_item)
        rel_dir_set.add(commissions_item_reldir(comm_item))
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
    db_dict, citems, rel_dir_set = db_date_dictionary_comm_item(data_dir)
    sync_list = []
    for ci in db_dict:
        if ci not in disk_dict:
            sync_list.append(int(os.path.basename(ci).split('.')[0]))
    return sync_list


def sync_comm_item(session, f, comm_item):
    """
    writes xml file for commissions item
    """
    with open(f, 'wb')() as fh:
        fh.write(ET.tostring(comm_item.to_xml()))
    session.query(Citem).filter_by(id=comm_item.id).update({"last_sync_time": dt.now()})
    print('%s written' % f)


def delete_orphen_comm_items(session, comm_items):
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


def cache_comm_items(session, datadir):
    # Make query, assemble lists
    base_dir = os.path.join(datadir, 'transactions', 'invoices', 'invoice_items', 'commissions_items')
    disk_dict = directory_date_dictionary(base_dir)
    date_dict, citems, rel_dir_set = db_date_dictionary_comm_item(session, base_dir)
    verify_dirs_ready(date_dict)
    to_sync = []
    for comm_item in citems:
        #
        # Make sure destination directory if it doesn't exist
        #
        if comm_item.amount > 0:
            file = commissions_item_fullpathname(datadir, comm_item)
            # add to sync list if comm item not on disk
            if file not in disk_dict:
                to_sync.append(comm_item)
            else:
                # check the rest of the business rules for syncing
                # no time stamps, timestamps out of sync
                if comm_item.last_sync_time is None or comm_item.modified_date is None:
                    to_sync.append(comm_item)
                if comm_item.modified_date > comm_item.last_sync_time:
                    to_sync.append(comm_item)
    # Write out xml
    for comm_item in to_sync:
        f = commissions_item_fullpathname(datadir, comm_item)
        sync_comm_item(session, f, comm_item)


def cache_comm_payments(session, datadir, cache):
    for cm in comm_months(end=dt.now()):
        month = cm['month']
        year = cm['year']
        for employee in session.query(Employee).filter(Employee.salesforce == 1, Employee.active == 1):
            payments, commissions = \
                employee_commissions_transactions_year_month(session, employee, datadir, year, month, cache)
            for pay in payments:
                if pay.amount > 0:
                    filename, pay_m_y = archive.full_dated_obj_xml_path(datadir, pay)
                    if not os.path.isdir(os.path.dirname(filename)):
                        mkdirs(os.path.dirname(filename))
                    with open(filename, 'w') as fh:
                        fh.write(ET.tostring(pay.to_xml()))
                    print('%s written' % filename)


def iitem_to_xml(iitem):
    doc = ET.Element('invoice-item')

    ET.SubElement(doc, 'id').text = str(iitem.id)
    ET.SubElement(doc, 'invoice_id').text = str(iitem.invoice_id)
    desc_ele = ET.SubElement(doc, 'description')
    desc_ele.text = iitem.description
    desc_ele.set('Invoice', str(iitem.invoice_id))
    desc_ele.set('Amount', str(iitem.amount))
    desc_ele.set(
        'comm', '%s: %s-%s %s %s - %s' % (
            str(iitem.id), str(iitem.invoice.period_start),
            str(iitem.invoice.period_end),
            iitem.invoice.contract.employee.firstname,
            iitem.invoice.contract.employee.lastname, iitem.description))
    ET.SubElement(doc, 'amount').text = str(iitem.amount)
    ET.SubElement(doc, 'cost').text = str(iitem.cost)
    ET.SubElement(doc, 'quantity').text = str(iitem.quantity)
    ET.SubElement(doc, 'cleared').text = str(iitem.cleared)

    return doc


def prettify(elemstr):
    """
    Return a pretty-printed XML string for the Element.
    """
    reparsed = minidom.parseString(elemstr)
    return reparsed.toprettyxml(indent="  ")


def iitem_xml_pretty_str(iitem):
    xele = iitem_to_xml(iitem)
    return prettify(ET.tostring(xele))


def cache_invoice(datadir, inv):
    f, rel_dir = archive.full_non_dated_xml_obj_path(os.path.join(datadir, 'transactions', 'invoices'), inv)
    full_path = os.path.join(datadir, rel_dir)
    if not os.path.isdir(full_path):
        os.makedirs(full_path)
    with open(f, 'wb')() as fh:
        fh.write(ET.tostring(inv.to_xml()))

    print('%s written' % f)


def cache_invoices(session, datadir):
    for inv in sales_person_invoices_of_interest(session, sa_sheree(session)):
        cache_invoice(datadir, inv)


def cache_invoices_items(datadir, session, employee, cache):
    for inv in sales_person_invoices_of_interest(session, employee):
        for iitem in inv.invoice_items:
            f = archive.full_non_dated_xml_obj_path(datadir, iitem)
            with open(f, 'wb')() as fh:
                fh.write(iitem_xml_pretty_str(iitem))
            print('%s written' % f)
    iex = iitem_exclude(session, employee, datadir, cache)
    doc = ET.Element('excluded-invoice-items')
    for ix in iex:
        ET.SubElement(doc, 'hash').text = str(ix)
    ex_inv_filename = os.path.join(datadir, 'excludes.xml')
    with open(ex_inv_filename, 'w') as fh:
        fh.write(ET.tostring(doc))
    print('%s written' % ex_inv_filename)


def delete_old_voided_invoices(session, args):
    """
    voided invoices serve as reminders to ignore in the past 90 days
    :param session:
    :param args:
    :return:
    """
    vinvs = session.query(Invoice).filter(
        and_(Invoice.voided == 1, Invoice.period_end < dt.now() - td(days=args.days_back)))
    for inv in vinvs:
        session.delete(inv)
