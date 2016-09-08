import os
import xml.etree.ElementTree as ET
from datetime import datetime as dt

from s3_mysql_backup import mkdirs

from rrg.models import Invoice
from rrg.models import InvoicePayment
from rrg.models import Iitem
from rrg.models import ClientCheck
from rrg.models import Employee
from rrg.models import EmployeePayment
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
    f = full_non_dated_xml_path(data_dir, invoice)
    with open(f, 'w') as fh:
        fh.write(ET.tostring(invoice.to_xml()))

    session.query(Invoice).filter_by(id=invoice.id).update({"last_sync_time": dt.now()})
    print('%s written' % f)


def sync_invoice_item(session, data_dir, inv_item):
    """
    writes xml file for invoice item
    """
    f = full_non_dated_xml_path(data_dir, inv_item)
    with open(f, 'w') as fh:
        fh.write(ET.tostring(inv_item.to_xml()))

    session.query(Iitem).filter_by(id=inv_item.id).update({"last_sync_time": dt.now()})
    print('%s written' % f)


def sync_clients_check(session, data_dir, ccheck):
    """
    writes xml file for clients checks
    """
    f = full_non_dated_xml_path(data_dir, ccheck)
    with open(f, 'w') as fh:
        fh.write(ET.tostring(ccheck.to_xml()))

    session.query(ClientCheck).filter_by(id=ccheck.id).update(
        {"last_sync_time": dt.now()})
    print('%s written' % f)


def sync_invoice_payment(session, data_dir, ccheck):
    """
    writes xml file for invoice payment
    """
    f = full_non_dated_xml_path(data_dir, ccheck)
    with open(f, 'w') as fh:
        fh.write(ET.tostring(ccheck.to_xml()))

    session.query(InvoicePayment).filter_by(id=ccheck.id).update({"last_sync_time": dt.now()})
    print('%s written' % f)


def sync_employee(session, data_dir, e):
    """
    writes xml file for employee
    """
    f = full_non_dated_xml_path(data_dir, e)
    with open(f, 'w') as fh:
        fh.write(ET.tostring(e.to_xml()))
    session.query(Employee).filter_by(id=e.id).update({"last_sync_time": dt.now()})
    print('%s written' % f)


def sync_employee_payment(session, data_dir, ep):
    """
    writes xml file for employee payment
    """
    f = full_non_dated_xml_path(data_dir, ep)
    with open(f, 'w') as fh:
        fh.write(ET.tostring(ep.to_xml()))
    session.query(EmployeePayment).filter_by(id=ep.id).update({"last_sync_time": dt.now()})
    print('%s written' % f)


def db_date_dictionary_invoice(session, args):
    """
    returns database dictionary counter part to directory_date_dictionary for sync determination
    :param data_dir:
    :return:
    """

    inv_dict = {}
    invoices = session.query(Invoice).order_by(Invoice.id)

    for inv in invoices:
        f = full_non_dated_xml_path(args.datadir, inv)
        inv_dict[f] = inv.last_sync_time

    return inv_dict, invoices


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


def db_date_dictionary_invoices_payments(session, args):
    """
    returns database dictionary counter part to directory_date_dictionary for sync determination
    :param data_dir:
    :return:
    """

    ipay_dict = {}

    ipays = session.query(InvoicePayment).order_by(InvoicePayment.id)

    for ipay in ipays:
        f = full_non_dated_xml_path(args.datadir, ipay)
        ipay_dict[f] = ipay.last_sync_time

    return ipay_dict, ipays


def db_date_dictionary_employees(session, args):
    """
    returns database dictionary counter part to directory_date_dictionary for sync determination
    :param data_dir:
    :return:
    """
    e_dict = {}
    employees = session.query(Employee)
    for e in employees:
        f = full_non_dated_xml_path(args.datadir, e)
        e_dict[f] = e.last_sync_time
    return e_dict, employees


def db_date_dictionary_employees_payments(session, args):
    """
    returns database dictionary counter part to directory_date_dictionary for sync determination
    :param data_dir:
    :return:
    """
    ep_dict = {}
    employeespayments = session.query(EmployeePayment)
    for e in employeespayments:
        f = full_non_dated_xml_path(args.datadir, e)
        ep_dict[f] = e.last_sync_time
    return ep_dict, employeespayments


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
    date_dict, invoices = db_date_dictionary_invoice(session, args)

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
        sync_invoice(session, args.datadir, comm_item)


def cache_invoices_items(session, args):
    disk_dict = directory_date_dictionary(args.datadir)

    # Make query, assemble lists
    date_dict, inv_items = db_date_dictionary_invoice_items(session, args)

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
        sync_invoice_item(session, args.datadir, comm_item)


def cache_clients_checks(session, args):
    disk_dict = directory_date_dictionary(args.datadir)

    # Make query, assemble lists
    date_dict, client_checks = db_date_dictionary_client_checks(session, args)

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
        sync_clients_check(session, args.datadir, comm_item)


def cache_invoices_payments(session, args):
    disk_dict = directory_date_dictionary(args.datadir)

    # Make query, assemble lists
    date_dict, invoices_payments = db_date_dictionary_invoices_payments(session, args)

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
        sync_invoice_payment(session, args.datadir, comm_item)


def cache_employees(session, args):
    disk_dict = directory_date_dictionary(args.datadir)

    # Make query, assemble lists
    date_dict, employees = db_date_dictionary_employees(session, args)

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
        sync_employee(session, args.datadir, emp)



def cache_employees_payments(session, args):
    disk_dict = directory_date_dictionary(args.datadir)

    # Make query, assemble lists
    date_dict, employees_payments = db_date_dictionary_employees_payments(session, args)

    to_sync = []
    for ep in employees_payments:
        filename = full_non_dated_xml_path(args.datadir, e)
        # add to sync list if invoice not on disk
        if filename not in disk_dict:
            to_sync.append(ep)
        else:
            if ep.modified_date > ep.last_sync_time:
                to_sync.append(e)

    # Write out xml
    for ep in to_sync:
        sync_employee_payment(session, args.datadir, pe)
