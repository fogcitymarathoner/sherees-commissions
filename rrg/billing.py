import os
import xml.etree.ElementTree as ET
from datetime import datetime as dt

from s3_mysql_backup import mkdirs
from rrg.utils import directory_date_dictionary
from rrg.archive import full_non_dated_xml_obj_path

def sync(session, data_dir, ep, model, crypter):
    """
    writes xml file for contract
    """
    f = full_non_dated_xml_obj_path(data_dir, ep)
    with open(f, 'w') as fh:
        fh.write(ET.tostring(ep.to_xml(crypter)))
    session.query(model).filter_by(id=ep.id).update({"last_sync_time": dt.now()})
    print('%s written' % f)


def db_date_dictionary_model(session, model, destination_dir):
    """
    returns database dictionary counter part to directory_date_dictionary for sync determination
    :param data_dir:
    :return:
    """
    em_dict = {}
    m_items = session.query(model)
    for e in m_items:
        f = full_non_dated_xml_obj_path(destination_dir, e)
        em_dict[f] = e.last_sync_time
    return em_dict, m_items


def verify_dirs_ready(date_dict):
    """
    run through the list of commissions directories created by db_data_dictionary_comm_item()
    """
    for d in date_dict:
        mkdirs(os.path.dirname(d))


def cache_non_date_parsed(session, datadir, model, crypter):
    disk_dict = directory_date_dictionary(datadir)
    # Make query, assemble lists
    date_dict, items = db_date_dictionary_model(session, model, datadir)
    #
    # Make sure destination directories exist
    #
    verify_dirs_ready(datadir, [datadir])
    to_sync = []
    for item in items:
        file = full_non_dated_xml_obj_path(datadir, item)
        # add to sync list if invoice not on disk
        if file not in disk_dict:
            to_sync.append(item)
        else:
            # check the rest of the business rules for syncing
            # no time stamps, timestamps out of sync
            if item.last_sync_time is None or item.modified_date is None:
                to_sync.append(item)
                continue
            if item.modified_date > item.last_sync_time:
                to_sync.append(item)
    # Write out xml
    for item in to_sync:
        sync(session, datadir, item, model, crypter)
