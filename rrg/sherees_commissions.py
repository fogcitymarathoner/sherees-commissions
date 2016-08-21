import os
import re
from datetime import datetime as dt
from xml.etree import ElementTree
from tabulate import tabulate
from operator import itemgetter
import logging
from s3_mysql_backup import TIMESTAMP_FORMAT
from s3_mysql_backup import mkdirs
from s3_mysql_backup import YMD_FORMAT

from rrg.models import Employee
from rrg.models import Citem
from rrg.models import CommPayment
from rrg.models import Contract
from rrg.models import Invoice
from rrg.models import Iitem
from rrg.queries import sheree_notes_payments
from rrg.queries import sherees_notes

from rrg.utils import directory_date_dictionary


logging.basicConfig(filename='testing.log', level=logging.DEBUG)
logger = logging.getLogger('test')

monthly_statement_ym_header = '\n\n%s/%s - #########################################################\n'


def sheree_total_monies_owe(session, args):
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
        total, res = year_month_statement(session, args)
        total_commissions += total

    sherees_paychecks_due, iitems, total_payroll = remaining_payroll(session)
    out = ''
    if args.format == 'latex':
        report += '\n\section{Summary of Monies Due}\n'
        out += '\\begin{itemize}'
        out += '\\item Hourly Pay %.2f' % total_payroll
        out += '\\item Commissions %.2f' % total_commissions
        out += '\\item Notes %.2f' % total_notes
        out += '\\item Total %.2f' % (total_commissions + total_payroll + total_notes)
        out += '\\end{itemize}'
    else:
        dout = {
            'Hourly': 'Hourly Pay %.2f' % total_payroll,
            'Commissions': 'Commissions %.2f' % total_commissions,
            'Notes': 'Notes %.2f' % total_notes,
            'Total': 'Total %.2f' % (total_commissions + total_payroll + total_notes)
        }
        out = tabulate(dout, headers='keys')

    return out


def sherees_notes_report(session, args):
    """
    returns sherees notes report as a subsection
    :param session:
    :param args:
    :return:
    """
    if args.format not in ['plain', 'latex']:
        print('Wrong format')
        quit()

    notes_payments = sheree_notes_payments(session)
    notes = sherees_notes(session)

    logger.debug('notes')
    logger.debug(notes)
    logger.debug('notespayments')
    logger.debug(notes_payments)
    combined = []
    for np in notes_payments:
        if np.notes:
            notes = ''.join([i if ord(i) < 128 else ' ' for i in np.notes])
        else:
            notes = ''
        new_rec = [np.id, np.date, notes, np.amount, np.check_number]
        logger.debug('adding notepayment %s' % new_rec)
        combined.append(new_rec)
    for n in notes:
        if n.notes:
            notes = ''.join([i if ord(i) < 128 else ' ' for i in n.notes])
        else:
            notes = ''
        new_rec = [n.id, n.date, notes, n.amount, '']
        logger.debug('adding note %s' % new_rec)
        combined.append(new_rec)
    combined_sorted = sorted(combined, key=itemgetter(1))
    logger.debug('combined')
    logger.debug(combined)
    logger.debug('combined sorted')
    logger.debug(combined_sorted)
    res_dict_transposed = {
        'id': [i[0] for i in combined_sorted],
        'date': [i[1] for i in combined_sorted],
        'description': [i[2] for i in combined_sorted],
        'amount': [i[3] for i in combined_sorted],
        'balance': [i[3] for i in combined_sorted],
        'check_number': [i[4] for i in combined_sorted]
    }

    total = 0
    for i in xrange(0, len(res_dict_transposed['balance'])):
        total += float(res_dict_transposed['balance'][i])
        res_dict_transposed['balance'][i] = total

    if args.format == 'plain':
        return tabulate(res_dict_transposed, headers='keys', tablefmt='plain')
    elif args.format == 'latex':
        report = ''
        report += '\n\section{Notes}\n'
        report += tabulate(res_dict_transposed, headers='keys',tablefmt='latex')
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
    if args.format == 'plain':
        for cm in comm_months(end=dt.now()):
            report += monthly_statement_ym_header % (cm['month'], cm['year'])
            args.month = cm['month']
            args.year = cm['year']
            total, res = year_month_statement(session, args)
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
            report += tabulate(res_dict_transposed, headers='keys', tablefmt='psql')
    elif args.format == 'latex':
        report += '\n\section{Commissions}\n'
        for cm in comm_months(end=dt.now()):
            report += '\n\subsection{%s/%s}\n' % (cm['year'], cm['month'])
            args.month = cm['month']
            args.year = cm['year']
            total, res = year_month_statement(session, args)
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
                               tablefmt='latex').replace('tabular', 'longtable')

            # report += '\n\end{document}\n'

    return report


def sherees_commissions_transactions_year_month(session, args):
    return sherees_comm_payments_year_month(session, args), \
           sorted(sherees_comm_items_year_month(session, args),
                  key=lambda ci: dt.strptime(ci.findall('date')[0].text,
                                             TIMESTAMP_FORMAT))


def sherees_comm_items_year_month(session, args):
    """
    reads comm items from xml forest
    Args:
        session:
        args:

    Returns:

    """
    xml_comm_items = []
    dir = sherees_comm_path_year_month(session, args)
    for dirName, subdirList, fileList in os.walk(dir, topdown=False):

        for fname in fileList:
            filename = os.path.join(dir, dirName, fname)
            if re.search(
                    'transactions/invoices/invoice_items/commissions_items/[0-9]{4}/[0-9]{4}/[0-9]{0,1}[0-9]{0,1}/'
                    '[0-9]{5}\.xml$',
                    filename):
                xml_comm_items.append(Citem.from_xml(filename))

    return xml_comm_items


def sherees_comm_payments_year_month(session, args):
    m = int(args.month)
    y = int(args.year)
    if m < 12:
        nexty = y
        nextm = m + 1
    else:
        nexty = int(y) + 1
        nextm = 1

    return session.query(CommPayment) \
        .filter(CommPayment.employee == sa_sheree(session)) \
        .filter(CommPayment.date >= '%s-%s-01' % (y, m)) \
        .filter(CommPayment.date < '%s-%s-01' % (nexty, nextm)) \
        .filter(CommPayment.voided == False) \
        .order_by(CommPayment.date)


def sa_sheree(session):
    """
    return sheree's sa object
    """
    return \
        session.query(Employee).filter_by(firstname='sheree', salesforce=True)[
            0]


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


def sherees_comm_path_year_month(session, args):
    """
    path to comms directory per year per month
    Args:
        session:
        args:

    Returns:

    """
    sheree = sa_sheree(session)
    return os.path.join(args.datadir, str(sheree.id), str(args.year),
                        str(args.month).zfill(2))


def full_comm_item_xml_path(data_dir, comm_item):
    rel_dir = os.path.join(str(comm_item.employee_id),
                           str(comm_item.date.year),
                           str(comm_item.date.month).zfill(2))
    return os.path.join(data_dir, rel_dir,
                        '%s.xml' % str(comm_item.id).zfill(5)), rel_dir


def db_date_dictionary_comm_item(session, args):
    """
    returns database dictionary counter part to directory_date_dictionary for sync determination
    :param data_dir:
    :return:
    """

    citem_dict = {}
    rel_dir_set = set()
    citems = session.query(Citem).order_by(Citem.id)

    for comm_item in citems:
        f, rel_dir = full_comm_item_xml_path(args.datadir, comm_item)
        rel_dir_set.add(rel_dir)
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
    f, rel_dir = full_comm_item_xml_path(data_dir, comm_item)
    with open(f, 'w') as fh:
        fh.write(ElementTree.tostring(comm_item.to_xml()))

    session.query(Citem).filter_by(id=comm_item.id).update(
        {"last_sync_time": dt.now()})
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


def cache_comm_items(session, args):
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
        'voided': int(citem.findall('voided')[0].text)
    }


def comm_item_xml_to_sa(citem):
    ci_dict = comm_item_xml_to_dict(citem)
    return Citem(id=ci_dict['id'], date=ci_dict['date'],
                 description=ci_dict['description'], amount=ci_dict['amount'],
                 employee_id=ci_dict['employee_id'], voided=ci_dict['voided'])


def year_month_statement(session, args):
    sum = 0
    res = []

    payments, commissions = \
        sherees_commissions_transactions_year_month(session, args)
    for payment in payments:
        res.append({
            'id': payment.check_number, 'date': payment.date,
            'description': payment.description,
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
