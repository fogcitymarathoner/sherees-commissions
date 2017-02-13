import re
import os
from datetime import datetime as dt
from sqlalchemy import and_
from tabulate import tabulate
from operator import itemgetter
import xml.etree.ElementTree as ET

from s3_mysql_backup import YMD_FORMAT
from s3_mysql_backup import TIMESTAMP_FORMAT

from rrg.archive import employee as archived_employee
from rrg.models import ContractItemCommItem
from rrg.commissions import comm_months
from rrg.commissions import salesperson_year_month_statement
from rrg.commissions import employee_commissions_transactions_year_month
from rrg.models import Employee
from rrg.models import Citem
from rrg.models import CommPayment
from rrg.models import Invoice
from rrg.payroll import remaining_payroll
from rrg.payroll import employee_payroll_due_report
from rrg.queries import salespersons_notes_payments
from rrg.sales import salespersons_notes
from rrg.utils import monthy_statement_ym_header

ledger_line_format = '%s %s %s %s'
monthly_statement_ym_header = '\n\n%s/%s - #########################################################\n'

# fixme: document this!
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
            m += 1
        else:
            m = 1
            y += 1
        date = dt(year=y, month=m, day=1)
    return year_months


def sales_person_contracts_of_interest(session, sales_person):
    contract_citems = session.query(ContractItemCommItem).filter(ContractItemCommItem.employee == sales_person)
    contracts = []
    for ci in contract_citems:
        if ci.contract_item.contract not in contracts:
            contracts.append(ci.contract_item.contract)
    return contracts


def sales_person_invoices_of_interest(session, sales_person):
    contracts = sales_person_contracts_of_interest(session, sales_person)
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


def salesperson_year_month_statement(session, employee, datadir, year, month, cache):
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


def sales_person_commissions_report(session, employee, cache, datadir, format):
    if args.format not in ['plain', 'latex']:
        print('Wrong format')
        quit()
    balance = 0
    report = str()
    if format == 'plain':
        for cm in comm_months(end=dt.now()):
            report += monthly_statement_ym_header % (cm['month'], cm['year'])
            month = cm['month']
            year = cm['year']
            total, res = salesperson_year_month_statement(session, employee, datadir, year, month, cache)
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
            month = cm['month']
            year = cm['year']
            total, res = salesperson_year_month_statement(session, employee, datadir, year, month, cache)
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
            report += tabulate(res_dict_transposed, headers='keys', tablefmt='latex').replace('tabular', 'longtable')

            # report += '\n\end{document}\n'

    return report


def monthly_summaries(session):

    salespeople = session.query(Employee).filter(Employee.salesforce==True)
    for salesperson in salespeople:
        balance = 0
        for cm in comm_months(end=dt.now()):
            print('%s %s' % (salesperson.firstname, salesperson.lastname))
            print(monthy_statement_ym_header % (cm['month'], cm['year']))
            year = cm['year']
            month = cm['month']
            total, res = employee_year_month_statement(session, salesperson, args.datadir, year, month, args.cache)
            balance += total
            res_dict_transposed = {
                'id': [''],
                'date': ['%s/%s' % (cm['month'], cm['year'])],
                'description': ['New Balance: %s' % balance],
                'amount': ['Period Total %s' % total]
            }
            print(tabulate(res_dict_transposed, headers='keys', tablefmt='plain'))


def monthly_detail(session, emp_id, datadir, year, month, cache):
    print(monthy_statement_ym_header % (year, month))
    employee_dict = archived_employee(emp_id, datadir)
    if employee_dict['salesforce']:
        employee = session.query(Employee).filter(Employee.id == employee_dict['id']).first()
        total, res = employee_year_month_statement(session, employee, datadir, year, month, cache)
        print('Total %s ' % total)
        for i in res:
            print(ledger_line_format % (i['id'], i['date'], i['description'], i['amount']))
    else:
        print('%s %s is not a sales person' % (employee_dict['firstname'], employee_dict['lastname']))


def employee_total_monies_owed(session, args):
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


def employee_notes_report_db(session, employee, format):
    """
    returns sherees notes report as a subsection
    :param session:
    :param args:
    :return:
    """
    if format not in ['plain', 'latex']:
        print('Wrong format - %s' % format)
        quit()

    notes_payments = salespersons_notes_payments(session, employee)
    notes = salespersons_notes(session, employee)

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


def invoice_report_month_year(datadir, month, year):
    invdir = os.path.join(datadir, 'transactions', 'invoices',
                          'invoice_items',
                          'commissions_items', 'invoices',
                          str(year), str(month).zfill(2))
    inv_items_dir = os.path.join(datadir, 'transactions', 'invoices',
                                 'invoice_items',
                                 'commissions_items', 'invoices',
                                 'invoices_items')
    if format == 'latex':
        res = ''
        res += '\n\subsection{Invoices %s/%s}\n' % (year, month)
    else:
        res = '%s/%s #######################\n' % (year, month)
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
                        if format == 'plain':
                            res += '\t\t%s cost: \char36 %.2f quantity: %s amount: \char36 %.2f\n' % (
                                description, cost, quantity, amount)
                        else:
                            res += '\n\hspace{20mm}%s cost: \char36 %.2f quantity: %s amount: \char36 %.2f' \
                                   ' \\newline \n' % (
                                       description, cost, quantity, amount)
    return res


def invoices_items(session, employee):
    """
    gathers a list of all of the sales persons invoice items of interest
    :param session:
    :return:
    """
    iitems = []
    for inv in sales_person_invoices_of_interest(session, employee):
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


def cached_comm_items(session, employee, datadir, cache):
    citems = []
    for cm in comm_months(end=dt.now()):
        month = cm['month']
        year = cm['year']
        total, res = salesperson_year_month_statement(session, employee, datadir, year, month, cache)
        for ci in res:
            try:
                if ci.description not in citems and ci.description.lower == 'overtime':
                    citems.append(ci.description)
            except AttributeError:
                pass
    return citems


def iitem_exclude(session, employee, datadir, cache):
    iitems = invoices_items(session, employee)
    citems = cached_comm_items(session, employee, datadir, cache)
    ex = {}
    for i in iitems:
        if i not in citems:
            ex[hash(i['description'])] = None
    return ex


def inv_report(session, employee, datadir, cache, format):
    if cache:
        res = ''
        if format == 'plain':
            for cm in comm_months(end=dt.now()):
                month = cm['month']
                year = cm['year']
                res += invoice_report_month_year(datadir, month, year)
        else:
            res = '\n\section{Invoices}\n'
            for cm in comm_months(end=dt.now()):
                month = cm['month']
                year = cm['year']
                res += invoice_report_month_year(datadir, month, year)
        return res
    else:
        iex = iitem_exclude(session, employee, datadir, cache)
        invs = sales_person_invoices_of_interest(session, employee)
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


def money_due(session, employee, datadir, cache, format):
    report = ''
    if format == 'plain':
        report += 'Summary\n'
        report += total_monies_owed(session, employee, datadir, cache, format)
        report += '\n'
        report += 'Hourly\n'
        report += employee_payroll_due_report(session, employee, format)
        report += '\n'
        report += 'Notes Report\n'
        report += employee_notes_report_db(session, employee, format)
        report += '\n'
        report += 'Commissions Report\n'
        report += sales_person_commissions_report(session, employee, datadir, cache, format)
        report += '\n'
        report += 'Invoices Report\n'
        report += inv_report(session, employee, datadir, cache, format)
    elif format == 'latex':
        report += comm_latex_document_header("Sheree's Monies Due Report")
        report += total_monies_owed(session, employee, datadir, cache, format)
        report += '\n'
        report += employee_payroll_due_report(session, employee, format)
        report += '\n'
        # fixme: cached notes never written
        report += employee_notes_report_db(session, employee, format)
        report += '\n'
        report += sales_person_commissions_report(session, employee, datadir, cache, format)
        report += '\n'
        report += inv_report(session, employee, datadir, cache, format)
        report += '\n\end{document}\n'


def total_monies_owed(session, employee, datadir, cache, format):

    notes = salespersons_notes(session, employee)
    notes_payments = salespersons_notes_payments(session, employee)

    amounts = [-np.amount for np in notes_payments] + [n.amount for n in notes]
    total_notes = 0
    for a in amounts:
        total_notes += a
    total_commissions = 0
    for cm in comm_months(end=dt.now()):
        month = cm['month']
        year = cm['year']
        total, res = salesperson_year_month_statement(
            session, employee, datadir, year, month, cache)
        total_commissions += total
    sherees_paychecks_due, iitems, total_payroll = remaining_payroll(session, employee)
    out = ''
    if format == 'latex':
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
                    '[0-9]{5}\.xml$', filename):
                xml_comm_items.append(Citem.from_xml(filename))
    return xml_comm_items


def employee_commissions_transactions_year_month(session, employee, datadir, year, month, cache):
    return employee_comm_payments_year_month(session, employee, datadir, year, month, cache), \
           sorted(employee_comm_items_year_month(employee, datadir, year, month),
                  key=lambda ci: dt.strptime(ci.findall('date')[0].text, TIMESTAMP_FORMAT))
