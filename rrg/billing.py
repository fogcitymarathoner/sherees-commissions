import os
import xml.etree.ElementTree as ET
from datetime import datetime as dt

from s3_mysql_backup import mkdirs

from rrg.models import Invoice
from rrg.models import InvoicePayment
from rrg.models import Iitem
from rrg.models import Client
from rrg.models import ClientCheck
from rrg.models import ClientMemo
from rrg.models import ClientManager
from rrg.models import Employee
from rrg.models import EmployeeMemo
from rrg.models import EmployeePayment
from rrg.models import Contract
from rrg.models import ContractItem
from rrg.utils import directory_date_dictionary
from rrg.utils import transactions_invoices_dir
from rrg.utils import clients_dir
from rrg.utils import clients_managers_dir
from rrg.utils import clients_memos_dir
from rrg.utils import clients_checks_dir
from rrg.utils import employees_dir
from rrg.utils import commissions_payment_dir
from rrg.utils import contracts_items_dir
from rrg.utils import contracts_dir
from rrg.utils import employees_memos_dir
from rrg.utils import employees_payments_dir


def full_dated_obj_xml_path(data_dir, obj):
    rel_dir = os.path.join(str(obj.date.year), str(obj.date.month).zfill(2))
    return os.path.join(data_dir, rel_dir, '%s.xml' % str(obj.id).zfill(5)), rel_dir


def full_non_dated_xml_path(data_dir, obj):
    return os.path.join(data_dir, '%s.xml' % str(obj.id).zfill(5))


def full_non_dated_xml_id_path(data_dir, id):
    return os.path.join(data_dir, '%s.xml' % str(id).zfill(5))


def sync(session, data_dir, ep, model, crypter):
    """
    writes xml file for contract
    """
    f = full_non_dated_xml_path(data_dir, ep)
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
        f = full_non_dated_xml_path(destination_dir, e)
        em_dict[f] = e.last_sync_time
    return em_dict, m_items


def verify_dirs_ready(data_dir, rel_dir_set):
    """
    run through the list of commissions directories created by db_data_dictionary_comm_item()
    """
    for d in rel_dir_set:
        dest = os.path.join(data_dir, d)
        mkdirs(dest)


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
        file = full_non_dated_xml_path(datadir, item)
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
