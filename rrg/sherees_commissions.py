import os
import re
from datetime import datetime as dt
from datetime import timedelta as td
import xml.etree.ElementTree as ET
from xml.dom import minidom
from tabulate import tabulate
from operator import itemgetter
from sqlalchemy import and_

from s3_mysql_backup import TIMESTAMP_FORMAT
from s3_mysql_backup import YMD_FORMAT
from s3_mysql_backup import mkdirs

from rrg.archive import full_dated_obj_xml_path
from rrg.archive import full_non_dated_xml_obj_path
from rrg.billing import verify_dirs_ready
from rrg.models import Employee
from rrg.models import Citem
from rrg.models import CommPayment
from rrg.models import ContractItemCommItem
from rrg.models import Contract
from rrg.models import Invoice
from rrg.models import Iitem
from rrg.queries import sheree_notes_payments
from rrg.queries import sherees_notes
from rrg.utils import directory_date_dictionary
from rrg.utils import commissions_items_dir
from rrg.utils import commissions_item_dir
from rrg.utils import transactions_invoices_dir

monthly_statement_ym_header = '\n\n%s/%s - #########################################################\n'


def sheree_total_monies_owed(session, args):
    notes = sherees_notes(session)

    notes_payments = sheree_notes_payments(session)
    amounts = [-np.amount for np in notes_payments] + [n.amount for n in notes]

    total_notes = 0
    for a in amounts:
        total_notes += a

    total_commissions = 0
    for cm in comm_months(end=dt.now()):
        args.month = cm['month']
        args.year = cm['year']
        total, res = employee_year_month_statement(
            session, args.employee, args.datadir, args.year, args.month, args.cache)
        total_commissions += total

    sherees_paychecks_due, iitems, total_payroll = remaining_payroll(session)
    out = ''
    if args.format == 'latex':
        out += '\n\section{Summary of Monies Due}\n'
        out += '\\begin{itemize}'
        out += '\\item Hourly Pay %.2f' % total_payroll
        out += '\\item Commissions %.2f' % total_commissions
        out += '\\item Notes %.2f' % total_notes
        out += '\\item Total %.2f' % (
            total_commissions + total_payroll + total_notes)
        out += '\\end{itemize}'
    else:
        dout = {
            'Hourly': ['Hourly Pay %.2f' % total_payroll],
            'Commissions': ['Commissions %.2f' % total_commissions],
            'Notes': ['Notes %.2f' % total_notes],
            'Total': ['Total %.2f' % (
                total_commissions + total_payroll + total_notes)]
        }
        out = tabulate(dout, headers='keys')

    return out


def sherees_notes_report_db(session, format):
    """
    returns sherees notes report as a subsection
    :param session:
    :param args:
    :return:
    """
    if format not in ['plain', 'latex']:
        print('Wrong format')
        quit()

    sheree = sa_sheree(session)
    notes_payments = sheree_notes_payments(session, sheree)
    notes = sherees_notes(session, sheree)

    combined = []
    for np in notes_payments:
        if np.notes:
            notestx = ''.join([i if ord(i) < 128 else ' ' for i in np.notes])
        else:
            notestx = ''
        new_rec = [np.id, np.date, notestx, -np.amount, np.check_number]
        combined.append(new_rec)
    for n in notes:
        if n.notes:
            notestx = ''.join([i if ord(i) < 128 else ' ' for i in n.notes])
        else:
            notestx = ''
        new_rec = [n.id, n.date, notestx, n.amount, '']
        combined.append(new_rec)
    combined_sorted = sorted(combined, key=itemgetter(1))

    res_dict_transposed = {
        'id': [i[0] for i in combined_sorted],
        'date': [dt.strftime(i[1], '%m/%d/%Y') for i in combined_sorted],
        'description': [i[2] for i in combined_sorted],
        'amount': ["%.2f" % round(i[3], 2) for i in combined_sorted],
        'balance': [i[3] for i in combined_sorted],
        'check_number': [i[4] for i in combined_sorted]
    }

    total = 0
    for i in xrange(0, len(res_dict_transposed['balance'])):
        total += float(res_dict_transposed['balance'][i])
        res_dict_transposed['balance'][i] = "%.2f" % round(total, 2)

    if format == 'plain':
        return tabulate(res_dict_transposed, headers='keys', tablefmt='plain')
    elif format == 'latex':
        report = ''
        report += '\n\section{Notes}\n'
        report += tabulate(res_dict_transposed, headers='keys',
                           tablefmt='latex')
        return report.replace('tabular', 'longtable')


def comm_latex_document_header(title='needs title'):
    report = ''
    report += '\documentclass[11pt, a4paper]{report}\n'

    report += '\usepackage{booktabs}\n'
    report += '\usepackage{ltxtable}\n'

    report += '\\begin{document}\n'
    report += '\\title{%s - %s}\n' % (dt.strftime(dt.now(), '%m/%d/%Y'), title)
    report += '\\maketitle\n'
    report += '\\tableofcontents\n'
    report += '\\newpage\n'
    return report


def sherees_commissions_report(session, args):
    if args.format not in ['plain', 'latex']:
        print('Wrong format')
        quit()
    balance = 0
    report = str()
    employee = session.query(Employee).filter(Employee.id == 1025).first()
    if args.format == 'plain':
        for cm in comm_months(end=dt.now()):
            report += monthly_statement_ym_header % (cm['month'], cm['year'])
            args.month = cm['month']
            args.year = cm['year']
            total, res = employee_year_month_statement(
                session, employee, args.datadir, args.year, args.month, args.cache)
            balance += total
            res_dict_transposed = {
                'id': map(lambda x: x['id'], res),
                'date': map(lambda x: x['date'], res),
                'description': map(lambda x: x['description'], res),
                'amount': map(lambda x: x['amount'], res)
            }
            res_dict_transposed['id'].append('')
            res_dict_transposed['date'].append('')
            res_dict_transposed['description'].append(
                'New Balance: %s' % balance)
            res_dict_transposed['amount'].append('Period Total %s' % total)
            report += tabulate(res_dict_transposed, headers='keys',
                               tablefmt='psql')
    elif args.format == 'latex':
        report += '\n\section{Commissions}\n'
        for cm in comm_months(end=dt.now()):
            report += '\n\subsection{%s/%s}\n' % (cm['year'], cm['month'])
            args.month = cm['month']
            args.year = cm['year']
            total, res = employee_year_month_statement(
                session, employee, args.datadir, args.year, args.month, args.cache)
            balance += total
            res_dict_transposed = {
                'id': map(lambda x: x['id'], res),
                'date': map(lambda x: x['date'], res),
                'description': map(lambda x: x['description'], res),
                'amount': map(lambda x: x['amount'], res)
            }
            res_dict_transposed['id'].append('')
            res_dict_transposed['date'].append('')
            res_dict_transposed['description'].append(
                'New Balance: %s' % balance)
            res_dict_transposed['amount'].append(total)
            report += tabulate(res_dict_transposed, headers='keys',
                               tablefmt='latex').replace('tabular',
                                                         'longtable')

            # report += '\n\end{document}\n'

    return report


def employee_commissions_transactions_year_month(session, employee, datadir, year, month, cache):
    return employee_comm_payments_year_month(session, employee, datadir, year, month, cache), \
           sorted(employee_comm_items_year_month(employee, datadir, year, month),
                  key=lambda ci: dt.strptime(ci.findall('date')[0].text, TIMESTAMP_FORMAT))


def employee_comm_items_year_month(employee, datadir, year, month):
    """
    reads comm items from xml forest
    Args:
        session:
        args:

    Returns:

    """
    xml_comm_items = []
    dir = employee_comm_path_year_month(employee, datadir, year, month)
    for dirName, subdirList, fileList in os.walk(dir, topdown=False):
        for fname in fileList:
            filename = os.path.join(dir, dirName, fname)
            if re.search(
                    'transactions/invoices/invoice_items/commissions_items/[0-9]{5}/[0-9]{4}/[0-9]{0,1}[0-9]{0,1}/'
                    '[0-9]{5}\.xml$',
                    filename):
                xml_comm_items.append(Citem.from_xml(filename))
    return xml_comm_items


def employee_comm_payments_year_month(session, employee, datadir, year, month, cache):
    m = int(month)
    y = int(year)
    if m < 12:
        nexty = y
        nextm = m + 1
    else:
        nexty = int(y) + 1
        nextm = 1
    if not cache:
        return session.query(CommPayment) \
            .filter(CommPayment.employee == employee) \
            .filter(CommPayment.date >= '%s-%s-01' % (y, m)) \
            .filter(CommPayment.date < '%s-%s-01' % (nexty, nextm)) \
            .filter(CommPayment.voided == False) \
            .order_by(CommPayment.date).all()
    else:
        cps = []
        dirname = os.path.join(
            datadir, 'transactions', 'invoices', 'invoice_items', 'commissions_payments', str(y), str(m).zfill(2))
        for dirName, subdirList, fileList in os.walk(dirname, topdown=False):
            for fn in fileList:
                fullname = os.path.join(dirName, fn)
                doc = CommPayment.from_xml(fullname)
                amount = float(doc.findall('amount')[0].text)
                check_number = doc.findall('check_number')[0].text
                description = doc.findall('description')[0].text
                date = doc.findall('date')[0].text
                cps.append(
                    CommPayment(amount=amount, check_number=check_number,
                                description=description, date=date))
        return cps


def sa_sheree(session):
    """
    return sheree's sa object
    """
    return \
        session.query(Employee).filter_by(firstname='sheree', salesforce=True)[0]


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


def employee_comm_path_year_month(employee, datadir, year, month):
    """
    path to comms directory per year per month
    Args:
        session:
        args:

    Returns:

    """
    return os.path.join(
        datadir, 'transactions', 'invoices', 'invoice_items', 'commissions_items',
        str(employee.id).zfill(5), str(year), str(month).zfill(2))


def db_date_dictionary_comm_item(session, datadir):
    """
    returns database dictionary counter part to directory_date_dictionary for sync determination
    :param data_dir:
    :return:
    """
    citem_dict = {}
    rel_dir_set = set()
    citems = session.query(Citem).order_by(Citem.id)
    for comm_item in citems:
        f, _ = full_dated_obj_xml_path(commissions_item_dir(datadir, comm_item), comm_item)
        rel_dir_set.add(os.path.dirname(f.replace(datadir, '')[1:len(f.replace(datadir, ''))]))
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


def sync_comm_item(session, data_dir, comm_item):
    """
    writes xml file for commissions item
    """
    f = os.path.join(data_dir, '%s.xml' % str(comm_item.id).zfill(5))
    with open(f, 'w') as fh:
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
    disk_dict = directory_date_dictionary(commissions_items_dir(datadir))
    date_dict, citems, rel_dir_set = db_date_dictionary_comm_item(session, commissions_items_dir(datadir))
    to_sync = []
    for comm_item in citems:
        #
        # Make sure destination directory if it doesn't exist
        #
        comm_item_dir = commissions_item_dir(datadir, comm_item)
        if comm_item.amount > 0:
            verify_dirs_ready(comm_item_dir, [comm_item_dir])
            file = os.path.join(comm_item_dir, '%s.xml' % str(comm_item.id).zfill(5))
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
        sync_comm_item(session, commissions_item_dir(datadir, comm_item), comm_item)


def cache_comm_payments(session, datadir, cache):
    for cm in comm_months(end=dt.now()):
        month = cm['month']
        year = cm['year']
        for employee in session.query(Employee).filter(Employee.salesforce == 1, Employee.active == 1):
            payments, commissions = \
                employee_commissions_transactions_year_month(session, employee, datadir, year, month, cache)
            for pay in payments:
                if pay.amount > 0:
                    filename, pay_m_y = full_dated_obj_xml_path(datadir, pay)
                    if not os.path.isdir(os.path.dirname(filename)):
                        mkdirs(os.path.dirname(filename))
                    with open(filename, 'w') as fh:
                        fh.write(ET.tostring(pay.to_xml()))
                    print('%s written' % filename)


def comm_item_xml_to_dict(citem):
    """
    returns dictionary from xml comm doc root
    generated from from_xml(xml_file_name)
    this function does not work in models??? date is casted as a VisitableType from SQLAlchemy
    """
    date_str = citem.findall('date')[0].text
    return {
        'id': citem.findall('id')[0].text,
        'date': dt.strptime(date_str, TIMESTAMP_FORMAT),
        'description': citem.findall('description')[0].text,
        'amount': round(float(citem.findall('amount')[0].text)),
        'employee_id': citem.findall('employee_id')[0].text,
        'voided': True if citem.findall('voided')[0].text == 'True' else False
    }


def comm_item_xml_to_sa(citem):
    ci_dict = comm_item_xml_to_dict(citem)
    return Citem(id=ci_dict['id'], date=ci_dict['date'],
                 description=ci_dict['description'], amount=ci_dict['amount'],
                 employee_id=ci_dict['employee_id'], voided=ci_dict['voided'])


def employee_year_month_statement(session, employee, datadir, year, month, cache):
    """
    returns employee/salespersons commissison for particular year/month either from db or xml tree
    :param session:
    :param employee:
    :param datadir:
    :param year:
    :param month:
    :param cache:
    :return:
    """
    sum = 0
    res = []
    payments, commissions = employee_commissions_transactions_year_month(session, employee, datadir, year, month, cache)
    for payment in payments:
        res.append({
            'id': payment.check_number, 'date': payment.date, 'description': payment.description,
            'amount': -payment.amount, 'employee_id': payment.employee_id})
        sum -= payment.amount
    for citem in commissions:
        ci = comm_item_xml_to_sa(citem)
        if ci.voided != 1:
            res.append({
                'id': '',
                'date': dt.strftime(ci.date, YMD_FORMAT),
                'description': ci.description,
                'amount': round(ci.amount),
                'employee_id': ci.employee_id,
            })
            sum += ci.amount
    return sum, res


def remaining_payroll(session):
    """
    gather sherees remaining payroll with invoice and invoice items lists to
    use to exclude from deletion
    """

    scontract = \
        session.query(Contract).filter(
            Contract.employee == sa_sheree(session))[2]
    sherees_paychecks_due = session.query(Invoice).filter(
        Invoice.contract == scontract, Invoice.voided == 0,
        Invoice.prcleared == 0, Invoice.posted == 1)
    do_not_delete_items = []
    total_due = 0
    for pc in sherees_paychecks_due:
        iitems = session.query(Iitem).filter(Iitem.invoice == pc)
        pay = 0
        for i in iitems:
            do_not_delete_items.append(i)
            pay += i.quantity * i.cost
        total_due += pay
    return sherees_paychecks_due, do_not_delete_items, total_due


def payroll_due_report(session, args):
    """
    """
    sherees_paychecks_due, iitems, total = remaining_payroll(session)
    res = dict(id=[], date=[], description=[], amount=[])
    res['id'] = [i.id for i in sherees_paychecks_due]
    res['date'] = [i.date for i in sherees_paychecks_due]
    res['description'] = [i.period_start for i in sherees_paychecks_due]
    for pc in sherees_paychecks_due:
        pay = 0
        for i in pc.invoice_items:
            pay += i.quantity * i.cost
        res['amount'].append(pay)
    res['id'].append('')
    res['date'].append('')
    res['description'].append('Total Due')
    res['amount'].append(total)
    if args.format == 'plain':
        return tabulate(res, headers='keys', tablefmt='plain')
    elif args.format == 'latex':
        report = ''
        report += '\n\section{Hourly}\n'
        report += tabulate(res, headers='keys', tablefmt='latex')
        return report


def sherees_contracts_of_interest(session):
    contract_citems = session.query(ContractItemCommItem).filter(ContractItemCommItem.employee_id == 1024)
    contracts = []
    for ci in contract_citems:
        if ci.contract_item.contract not in contracts:
            contracts.append(ci.contract_item.contract)
    return contracts


def sherees_invoices_of_interest(session):
    contracts = sherees_contracts_of_interest(session)
    cids = []
    if contracts:
        for con in contracts:
            cids.append(con.id)
    invs = []
    if len(cids):
        invs = session.query(Invoice).filter(and_(Invoice.voided == False,
                                                  Invoice.contract_id.in_(cids))).order_by(Invoice.date)
    else:
        print('There are no invoices of sherees interest')
    return invs


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


def cache_invoice(args, inv):
    f, rel_dir = full_non_dated_xml_obj_path(transactions_invoices_dir(args.datadir), inv)
    full_path = os.path.join(args.datadir, rel_dir)
    if not os.path.isdir(full_path):
        os.makedirs(full_path)
    with open(f, 'w') as fh:
        fh.write(ET.tostring(inv.to_xml()))

    print('%s written' % f)


def cache_invoices(session, args):
    for inv in sherees_invoices_of_interest(session):
        cache_invoice(args, inv)


def cache_invoices_items(session, args):
    for inv in sherees_invoices_of_interest(session):
        for iitem in inv.invoice_items:
            f = full_non_dated_xml_obj_path(args.datadir, iitem)
            with open(f, 'w') as fh:
                fh.write(iitem_xml_pretty_str(iitem))
            print('%s written' % f)
    iex = iitem_exclude(session, args)
    doc = ET.Element('excluded-invoice-items')
    for ix in iex:
        ET.SubElement(doc, 'hash').text = str(ix)
    ex_inv_filename = os.path.join(args.datadir, 'excludes.xml')
    with open(ex_inv_filename, 'w') as fh:
        fh.write(ET.tostring(doc))
    print('%s written' % ex_inv_filename)


def invoices_items(session):
    """
    gathers a list of all of sherees invoice items of interest
    :param session:
    :return:
    """
    iitems = []
    for inv in sherees_invoices_of_interest(session):
        for iitem in inv.invoice_items:
            if iitem.invoice.voided is False:
                if iitem.quantity > 0:
                    if iitem.description.lower() == 'overtime':
                        iitems.append({
                            'id': iitem.id,
                            'date': iitem.invoice.date,
                            'description': '%s-%s %s %s - %s' % (
                                str(iitem.invoice.period_start),
                                str(iitem.invoice.period_end),
                                iitem.invoice.contract.employee.firstname,
                                iitem.invoice.contract.employee.lastname,
                                iitem.description)
                        })
    return iitems


def cached_comm_items(session, args):
    citems = []
    for cm in comm_months(end=dt.now()):
        args.month = cm['month']
        args.year = cm['year']
        total, res = employee_year_month_statement(session, args.employee, args.datadir, args.year, args.month,
                                                   args.cache)
        for ci in res:
            try:
                if ci.description not in citems and ci.description.lower == 'overtime':
                    citems.append(ci.description)
            except AttributeError:
                pass
    return citems


def iitem_exclude(session, args):
    iitems = invoices_items(session)
    citems = cached_comm_items(session, args)
    ex = {}
    for i in iitems:
        if i not in citems:
            ex[hash(i['description'])] = None
    return ex


def invoice_report_month_year(args):
    invdir = os.path.join(args.datadir, 'transactions', 'invoices',
                          'invoice_items',
                          'commissions_items', 'invoices',
                          str(args.year), str(args.month).zfill(2))
    inv_items_dir = os.path.join(args.datadir, 'transactions', 'invoices',
                                 'invoice_items',
                                 'commissions_items', 'invoices',
                                 'invoices_items')
    if args.format == 'latex':
        res = ''
        res += '\n\subsection{Invoices %s/%s}\n' % (args.year, args.month)
    else:
        res = '%s/%s #######################\n' % (args.year, args.month)
    for dirName, subdirList, fileList in os.walk(invdir, topdown=False):

        for fname in fileList:
            filename = os.path.join(dirName, fname)
            idoc = ET.parse(filename).getroot()
            iid = idoc.findall('id')[0].text
            idate = idoc.findall('date')[0].text
            employee = idoc.findall('employee')[0].text
            start = idoc.findall('period_start')[0].text
            end = idoc.findall('period_end')[0].text
            iitemsdoc = idoc.findall('invoice-items')
            res = ''
            total = 0
            iitemdocs_parsed = []
            for iitem_id_ele in iitemsdoc[0].findall('invoice-item'):
                iitemf = os.path.join(inv_items_dir,
                                      str(iitem_id_ele.text).zfill(6) + '.xml')
                iitemdoc = ET.parse(iitemf).getroot()
                iitemdocs_parsed.append(iitemdoc)
                quantity = float(iitemdoc.findall('quantity')[0].text)
                amount = float(iitemdoc.findall('amount')[0].text)
                total += quantity * amount
            if total > 0:
                if args.format == 'plain':
                    res += 'Invoice %s\n' % iid
                    res += '\t%s $%.2f %s %s-%s\n' % (
                        dt.strftime(dt.strptime(idate, TIMESTAMP_FORMAT), '%m/%d/%Y'),
                        total, employee,
                        dt.strftime(dt.strptime(start, TIMESTAMP_FORMAT), '%m/%d/%Y'),
                        dt.strftime(dt.strptime(end, TIMESTAMP_FORMAT), '%m/%d/%Y'))
                else:
                    res += 'Invoice %s \\newline \n' % iid
                    res += '\n\hspace{10mm}%s \char36 %.2f %s %s-%s \\newline \n' % (
                        dt.strftime(dt.strptime(idate, TIMESTAMP_FORMAT), '%m/%d/%Y'),
                        total, employee,
                        dt.strftime(dt.strptime(start, TIMESTAMP_FORMAT), '%m/%d/%Y'),
                        dt.strftime(dt.strptime(end, TIMESTAMP_FORMAT), '%m/%d/%Y'))
                for iitemdoc in iitemdocs_parsed:
                    cost = float(iitemdoc.findall('cost')[0].text)
                    quantity = float(iitemdoc.findall('quantity')[0].text)
                    amount = float(iitemdoc.findall('amount')[0].text)
                    description = iitemdoc.findall('description')[0].text
                    if float(amount) * float(quantity) > 0:
                        if args.format == 'plain':
                            res += '\t\t%s cost: \char36 %.2f quantity: %s amount: \char36 %.2f\n' % (
                                description, cost, quantity, amount)
                        else:
                            res += '\n\hspace{20mm}%s cost: \char36 %.2f quantity: %s amount: \char36 %.2f' \
                                   ' \\newline \n' % (
                                       description, cost, quantity, amount)

    return res


def inv_report(session, args):
    if args.cache:
        res = ''
        if args.format == 'plain':
            for cm in comm_months(end=dt.now()):
                args.month = cm['month']
                args.year = cm['year']
                res += invoice_report_month_year(args)
        else:
            res = '\n\section{Invoices}\n'
            for cm in comm_months(end=dt.now()):
                args.month = cm['month']
                args.year = cm['year']
                res += invoice_report_month_year(args)
        return res
    else:
        iex = iitem_exclude(session, args)
        invs = sherees_invoices_of_interest(session)
        for i in invs:
            total = 0
            for ii in i.invoice_items:
                if hash(ii.description) not in iex and ii.quantity > 0:
                    total += ii.quantity * ii.amount
                    print(ii)
            if total > 0:
                print(
                    '%s %s %s %s %s' % (
                        i.id, i.date, total, i.contract.employee.firstname,
                        i.contract.employee.lastname))


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
