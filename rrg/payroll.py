from tabulate import tabulate

from rrg.models import Contract
from rrg.models import Invoice
from rrg.models import Iitem


def remaining_payroll(session, employee):
    """
    gather sherees remaining payroll with invoice and invoice items lists to
    use to exclude from deletion
    """

    scontract = \
        session.query(Contract).filter(
            Contract.employee == employee)
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


def employee_payroll_due_report(session, employee, format):
    """
    """
    sherees_paychecks_due, iitems, total = remaining_payroll(session, employee)
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
    if format == 'plain':
        return tabulate(res, headers='keys', tablefmt='plain')
    elif format == 'latex':
        report = ''
        report += '\n\section{Hourly}\n'
        report += tabulate(res, headers='keys', tablefmt='latex')
        return report