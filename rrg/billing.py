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
from rrg.models import Employee
from rrg.models import EmployeeMemo
from rrg.models import EmployeePayment
from rrg.models import Contract
from rrg.models import ContractItem
from rrg.utils import directory_date_dictionary


def full_dated_obj_xml_path(data_dir, obj):
    rel_dir = os.path.join(str(obj.date.year), str(obj.date.month).zfill(2))
    return os.path.join(data_dir, rel_dir, '%s.xml' % str(obj.id).zfill(5)), rel_dir


def full_dated_comm_item_xml_path(data_dir, obj):
    rel_dir = os.path.join(str(obj.employee_id), str(obj.date.year), str(obj.date.month).zfill(2))
    return os.path.join(data_dir, rel_dir, '%s.xml' % str(obj.id).zfill(5)), rel_dir


def full_non_dated_xml_path(data_dir, obj):
    return os.path.join(data_dir, '%s.xml' % str(obj.id).zfill(5))


def sync(session, data_dir, ep, model):
    """
    writes xml file for contract
    """
    f = full_non_dated_xml_path(data_dir, ep)
    with open(f, 'w') as fh:
        fh.write(ET.tostring(ep.to_xml()))
    session.query(model).filter_by(id=ep.id).update({"last_sync_time": dt.now()})
    print('%s written' % f)


def db_date_dictionary_model(session, args, model):
    """
    returns database dictionary counter part to directory_date_dictionary for sync determination
    :param data_dir:
    :return:
    """
    em_dict = {}
    contract_items = session.query(model)
    for e in contract_items:
        f = full_non_dated_xml_path(args.datadir, e)
        em_dict[f] = e.last_sync_time
    return em_dict, contract_items


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
    date_dict, invoices = db_date_dictionary_model(session, args, Invoice)

    #
    # Make sure destination directories exist
    #
    verify_dirs_ready(args.datadir, [args.datadir])

    to_sync = []
    for inv in invoices:
        file = full_non_dated_xml_path(args.datadir, inv)
        # add to sync list if invoice not on disk
        if file not in disk_dict:
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
        sync(session, args.datadir, comm_item, Invoice)


def cache_invoices_items(session, args):
    disk_dict = directory_date_dictionary(args.datadir)

    # Make query, assemble lists
    date_dict, inv_items = db_date_dictionary_model(session, args, Iitem)

    to_sync = []
    for inv_item in inv_items:
        file = full_non_dated_xml_path(args.datadir, inv_item)
        # add to sync list if invoice not on disk
        if file not in disk_dict:
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
        sync(session, args.datadir, comm_item, Iitem)


def cache_clients_checks(session, args):
    disk_dict = directory_date_dictionary(args.datadir)

    # Make query, assemble lists
    date_dict, client_checks = db_date_dictionary_model(session, args, ClientCheck)

    to_sync = []
    for check in client_checks:
        file = full_non_dated_xml_path(args.datadir, check)
        # add to sync list if invoice not on disk
        if file not in disk_dict:
            to_sync.append(check)
        else:
            # check the rest of the business rules for syncing
            # no time stamps, timestamps out of sync
            if check.last_sync_time is None or check.modified_date is None:
                to_sync.append(check)
                continue
            if check.modified_date > check.last_sync_time:
                to_sync.append(check)

    # Write out xml
    for comm_item in to_sync:
        sync(session, args.datadir, comm_item, ClientCheck)


def cache_clients(session, args):
    disk_dict = directory_date_dictionary(args.datadir)

    # Make query, assemble lists
    date_dict, clients = db_date_dictionary_model(session, args, Client)

    to_sync = []
    for client in clients:
        file = full_non_dated_xml_path(args.datadir, client)
        # add to sync list if invoice not on disk
        if file not in disk_dict:
            to_sync.append(client)
        else:
            # check the rest of the business rules for syncing
            # no time stamps, timestamps out of sync
            if client.last_sync_time is None or client.modified_date is None:
                to_sync.append(client)
                continue
            if client.modified_date > client.last_sync_time:
                to_sync.append(client)

    # Write out xml
    for comm_item in to_sync:
        sync(session, args.datadir, comm_item, Client)


def cache_clients_memos(session, args):
    disk_dict = directory_date_dictionary(args.datadir)

    # Make query, assemble lists
    date_dict, client_memos = db_date_dictionary_model(session, args, ClientMemo)

    to_sync = []
    for check in client_memos:
        file = full_non_dated_xml_path(args.datadir, check)
        # add to sync list if invoice not on disk
        if file not in disk_dict:
            to_sync.append(check)
        else:
            # check the rest of the business rules for syncing
            # no time stamps, timestamps out of sync
            if check.last_sync_time is None or check.modified_date is None:
                to_sync.append(check)
                continue
            if check.modified_date > check.last_sync_time:
                to_sync.append(check)

    # Write out xml
    for comm_item in to_sync:
        sync(session, args.datadir, comm_item, ClientMemo)


def cache_invoices_payments(session, args):
    disk_dict = directory_date_dictionary(args.datadir)

    # Make query, assemble lists
    date_dict, invoices_payments = db_date_dictionary_model(session, args, InvoicePayment)

    to_sync = []
    for ipay in invoices_payments:
        file = full_non_dated_xml_path(args.datadir, ipay)
        # add to sync list if invoice not on disk
        if file not in disk_dict:
            to_sync.append(ipay)
        else:
            if ipay.modified_date > ipay.last_sync_time:
                to_sync.append(ipay)

    # Write out xml
    for comm_item in to_sync:
        sync(session, args.datadir, comm_item, InvoicePayment)


def cache_employees(session, args):
    disk_dict = directory_date_dictionary(args.datadir)

    # Make query, assemble lists
    date_dict, employees = db_date_dictionary_model(session, args, Employee)

    to_sync = []
    for e in employees:
        filename = full_non_dated_xml_path(args.datadir, e)
        # add to sync list if invoice not on disk
        if filename not in disk_dict:
            to_sync.append(e)
        else:
            if not e.modified_date or not e.last_sync_time:
                to_sync.append(e)
            elif e.modified_date > e.last_sync_time:
                to_sync.append(e)

    # Write out xml
    for emp in to_sync:
        sync(session, args.datadir, emp, Employee)


def cache_employees_payments(session, args):
    disk_dict = directory_date_dictionary(args.datadir)

    # Make query, assemble lists
    date_dict, employees_payments = db_date_dictionary_model(session, args, EmployeePayment)

    to_sync = []
    for ep in employees_payments:
        filename = full_non_dated_xml_path(args.datadir, ep)
        # add to sync list if invoice not on disk
        if filename not in disk_dict:
            to_sync.append(ep)
        else:
            if not ep.modified_date or not ep.last_sync_time:
                to_sync.append(ep)
            elif ep.modified_date > dt.date(ep.last_sync_time):
                to_sync.append(ep)

    # Write out xml
    for ep in to_sync:
        sync(session, args.datadir, ep, EmployeePayment)


def cache_employees_memos(session, args):
    disk_dict = directory_date_dictionary(args.datadir)

    # Make query, assemble lists
    date_dict, employees_memos = db_date_dictionary_model(session, args, EmployeeMemo)

    to_sync = []
    for ep in employees_memos:
        filename = full_non_dated_xml_path(args.datadir, ep)
        # add to sync list if invoice not on disk
        if filename not in disk_dict:
            to_sync.append(ep)
        else:
            if not ep.modified_date or not ep.last_sync_time:
                to_sync.append(ep)
            elif ep.modified_date > ep.last_sync_time:
                to_sync.append(ep)

    # Write out xml
    for ep in to_sync:
        sync(session, args.datadir, ep, EmployeeMemo)


def cache_contracts(session, args):
    disk_dict = directory_date_dictionary(args.datadir)

    # Make query, assemble lists
    date_dict, contracts = db_date_dictionary_model(session, args, Contract)

    to_sync = []
    for ep in contracts:
        filename = full_non_dated_xml_path(args.datadir, ep)
        # add to sync list if invoice not on disk
        if filename not in disk_dict:
            to_sync.append(ep)
        else:
            if not ep.modified_date or not ep.last_sync_time:
                to_sync.append(ep)
            elif ep.modified_date > ep.last_sync_time:
                to_sync.append(ep)

    # Write out xml
    for ep in to_sync:
        sync(session, args.datadir, ep, Contract)


def cache_contract_items(session, args):
    disk_dict = directory_date_dictionary(args.datadir)

    # Make query, assemble lists
    date_dict, contract_items = db_date_dictionary_model(session, args, ContractItem)

    to_sync = []
    for ep in contract_items:
        filename = full_non_dated_xml_path(args.datadir, ep)
        # add to sync list if invoice not on disk
        if filename not in disk_dict:
            to_sync.append(ep)
        else:
            if not ep.modified_date or not ep.last_sync_time:
                to_sync.append(ep)
            elif ep.modified_date > ep.last_sync_time:
                to_sync.append(ep)

    # Write out xml
    for ep in to_sync:
        sync(session, args.datadir, ep, ContractItem)
