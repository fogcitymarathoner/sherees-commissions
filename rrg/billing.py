import os
import xml.etree.ElementTree as ET
from datetime import datetime as dt
from rrg.models import Invoice
from rrg.utils import directory_date_dictionary

def full_invoice_xml_path(data_dir, invoice):
    return os.path.join(data_dir, '%s.xml' % str(invoice.id).zfill(4))


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


def cache_invoices(session, args):
    disk_dict = directory_date_dictionary(args.datadir)

    # Make query, assemble lists
    date_dict, citems, rel_dir_set = db_date_dictionary_comm_item(session,
                                                                  args)

    #
    # Make sure destination directories exist
    #
    verify_comm_dirs_ready(args.datadir, rel_dir_set)

    to_sync = []
    for comm_item in citems:
        file = full_comm_item_xml_path(args.datadir, comm_item)
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
        sync_comm_item(session, args.datadir, comm_item)

