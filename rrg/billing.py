import os
import xml.etree.ElementTree as ET
from datetime import datetime as dt

from s3_mysql_backup import mkdirs

from rrg.models import Invoice
from rrg.models import Iitem
from rrg.models import ClientCheck
from rrg.utils import directory_date_dictionary


def full_dated_obj_xml_path(data_dir, obj):
    rel_dir = os.path.join(str(obj.date.year), str(obj.date.month).zfill(2))
    return os.path.join(data_dir, rel_dir, '%s.xml' % str(obj.id).zfill(5)), rel_dir


def full_dated_comm_item_xml_path(data_dir, obj):
    rel_dir = os.path.join(str(obj.employee_id), str(obj.date.year), str(obj.date.month).zfill(2))
    return os.path.join(data_dir, rel_dir, '%s.xml' % str(obj.id).zfill(5)), rel_dir


def full_non_dated_xml_path(data_dir, obj):
    return os.path.join(data_dir, '%s.xml' % str(obj.id).zfill(5))


def sync_invoice(session, data_dir, invoice):
    """
    writes xml file for invoices
    """
    f, rel_dir = full_dated_obj_xml_path(data_dir, invoice)
    with open(f, 'w') as fh:
        fh.write(ET.tostring(invoice.to_xml()))

    session.query(Invoice).filter_by(id=invoice.id).update(
        {"last_sync_time": dt.now()})
    print('%s written' % f)


def sync_invoice_item(session, data_dir, inv_item):
    """
    writes xml file for invoices
    """
    f = full_non_dated_xml_path(data_dir, inv_item)
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
        f, rel_dir = full_dated_obj_xml_path(args.datadir, inv)
        rel_dir_set.add(rel_dir)
        inv_dict[f] = inv.last_sync_time

    return inv_dict, invoices, rel_dir_set


def db_date_dictionary_invoice_items(session, args):
    """
    returns database dictionary counter part to directory_date_dictionary for sync determination
    :param data_dir:
    :return:
    """

    invitem_dict = {}
    invoices_items = session.query(Iitem).order_by(Iitem.id)

    for invitem in invoices_items:
        f = full_non_dated_xml_path(args.datadir, invitem)
        invitem_dict[f] = invitem.last_sync_time

    return invitem_dict, invoices_items


def db_date_dictionary_client_checks(session, args):
    """
    returns database dictionary counter part to directory_date_dictionary for sync determination
    :param data_dir:
    :return:
    """

    cchecks_dict = {}

    clients_checks = session.query(ClientCheck).order_by(ClientCheck.id)

    for ccheck in clients_checks:
        f = full_non_dated_xml_path(args.datadir, ccheck)
        cchecks_dict[f] = ccheck.last_sync_time

    return cchecks_dict, clients_checks


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
        file = full_dated_obj_xml_path(args.datadir, inv)
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
    date_dict, inv_items = db_date_dictionary_invoice_items(session, args)

    to_sync = []
    for inv_item in inv_items:
        file = full_non_dated_xml_path(args.datadir, inv_item)
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


def cache_clients_checks(session, args):

    session.query(ClientCheck).all()