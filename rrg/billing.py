import os
import xml.etree.ElementTree as ET
from datetime import datetime as dt

from s3_mysql_backup import mkdirs

from rrg.models import Invoice
from rrg.utils import directory_date_dictionary


def full_invoice_xml_path(data_dir, invoice):
    return os.path.join(data_dir, '%s.xml' % str(invoice.id).zfill(4)), data_dir


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


def verify_invs_dir_ready(data_dir, rel_dir_set):
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
    verify_invs_dir_ready(args.datadir, rel_dir_set)

    to_sync = []
    for inv in invoices:
        file = full_invoice_xml_path(args.datadir, inv)
        # add to sync list if invoice not on disk
        if file[0] not in disk_dict:
            print('not on disk - building')
            to_sync.append(inv)
        else:
            # check the rest of the business rules for syncing
            # no time stamps, timestamps out of sync
            if inv.last_sync_time is None or inv.modified_date is None:
                print('no mod date - building')
                print('mod date %s' % inv.modified_date)
                print('sync %s' % inv.last_sync_time)
                to_sync.append(inv)
                continue
            if inv.modified_date > inv.last_sync_time:
                print('disk copy is old - building')
                to_sync.append(inv)

    # Write out xml
    for comm_item in to_sync:
        sync_invoice(session, args.datadir, comm_item)

