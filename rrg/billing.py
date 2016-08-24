import os
import xml.etree.ElementTree as ET
from datetime import datetime as dt

from s3_mysql_backup import mkdirs

from rrg.models import Invoice
from rrg.models import Iitem
from rrg.utils import directory_date_dictionary


def full_invoice_xml_path(data_dir, invoice):
    return os.path.join(data_dir, '%s.xml' % str(invoice.id).zfill(4)), data_dir


def full_invoice_item_xml_path(data_dir, invoice_item):
    return os.path.join(data_dir, '%s.xml' % str(invoice_item.id).zfill(4)), data_dir


def sync_invoice(session, data_dir, invoice):
    """
    writes xml file for invoices
    """
    f, rel_dir = full_invoice_xml_path(data_dir, invoice)
    with open(f, 'w') as fh:
        fh.write(ET.tostring(invoice.to_xml()))

    session.query(Invoice).filter_by(id=invoice.id).update(
        {"last_sync_time": dt.now()})
    print('%s written' % f)


def sync_invoice_item(session, data_dir, inv_item):
    """
    writes xml file for invoices
    """
    f, rel_dir = full_invoice_item_xml_path(data_dir, inv_item)
    with open(f, 'w') as fh:
        fh.write(ET.tostring(inv_item.to_xml()))

    session.query(Iitem).filter_by(id=inv_item.id).update(
        {"last_sync_time": dt.now()})
    print('%s written' % f)


def db_date_dictionary_invoice(session, args):
    """
    returns database dictionary counter part to directory_date_dictionary for sync determination
    :param data_dir:
    :return:
    """

    inv_dict = {}
    rel_dir_set = set()
    invoices = session.query(Invoice).order_by(Invoice.id)

    for inv in invoices:
        f, rel_dir = full_invoice_xml_path(args.datadir, inv)
        rel_dir_set.add(rel_dir)
        inv_dict[f] = inv.last_sync_time

    return inv_dict, invoices, rel_dir_set


def db_date_dictionary_invoice_items(session, args):
    """
    returns database dictionary counter part to directory_date_dictionary for sync determination
    :param data_dir:
    :return:
    """

    inv_dict = {}
    rel_dir_set = set()
    invoices_items = session.query(Iitem).order_by(Iitem.id)

    for invitem in invoices_items:
        f, rel_dir = full_invoice_xml_path(args.datadir, invitem)
        rel_dir_set.add(rel_dir)
        invitem_dict[f] = invitem.last_sync_time

    return inv_dict, invoices_items, rel_dir_set


def verify_dirs_ready(data_dir, rel_dir_set):
    """
    run through the list of commissions directories created by db_data_dictionary_comm_item()
    """
    for d in rel_dir_set:
        dest = os.path.join(data_dir, d)
        mkdirs(dest)


def cache_invoices(session, args):
    disk_dict = directory_date_dictionary(args.datadir)

    # Make query, assemble lists
    date_dict, invoices, rel_dir_set = db_date_dictionary_invoice(session, args)

    #
    # Make sure destination directories exist
    #
    verify_dirs_ready(args.datadir, rel_dir_set)

    to_sync = []
    for inv in invoices:
        file = full_invoice_xml_path(args.datadir, inv)
        # add to sync list if invoice not on disk
        if file[0] not in disk_dict:
            to_sync.append(inv)
        else:
            # check the rest of the business rules for syncing
            # no time stamps, timestamps out of sync
            if inv.last_sync_time is None or inv.modified_date is None:
                to_sync.append(inv)
                continue
            if inv.modified_date > inv.last_sync_time:
                to_sync.append(inv)

    # Write out xml
    for comm_item in to_sync:
        sync_invoice(session, args.datadir, comm_item)


def cache_invoices_items(session, args):
    disk_dict = directory_date_dictionary(args.datadir)

    # Make query, assemble lists
    date_dict, inv_items, rel_dir_set = db_date_dictionary_invoice_items(session, args)

    #
    # Make sure destination directories exist
    #
    verify_dirs_ready(args.datadir, rel_dir_set)

    to_sync = []
    for inv_item in inv_items:
        file = full_invoice_xml_path(args.datadir, inv_item)
        # add to sync list if invoice not on disk
        if file[0] not in disk_dict:
            to_sync.append(inv_item)
        else:
            # check the rest of the business rules for syncing
            # no time stamps, timestamps out of sync
            if inv_item.last_sync_time is None or inv_item.modified_date is None:
                to_sync.append(inv_item)
                continue
            if inv_item.modified_date > inv_item.last_sync_time:
                to_sync.append(inv_item)

    # Write out xml
    for comm_item in to_sync:
        sync_invoice_item(session, args.datadir, comm_item)

