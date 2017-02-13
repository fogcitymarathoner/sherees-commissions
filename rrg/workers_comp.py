"""
Routines for gathering timecard earnings between dates for Worker's comprehensive reporting.
Using SQL database data.
"""

from rrg.models import Invoice
from rrg.models import Iitem
from rrg.models import Contract


def wc_report(session, start_date, end_date):
    """
    get regular, overtime and doubletime earnings between start and end date
    inputs = start and end date
    output list like this
    [{"state": 'statename', "employees": [{'employee': 'employee_name', 'regular': #, 'overtime': #, 'doubletime': #}]
    """

    # get invoices
    invoices = session.query(Invoice).\
        join(Contract, Contract.id == Invoice.contract_id).\
        filter(
        Invoice.posted == 1, Invoice.voided == 0, Invoice.mock == 0, Invoice.cleared == 1, Invoice.prcleared == 1,
        Invoice.period_start >= start_date, Invoice.period_end < end_date)
    employees = set()
    states = set()
    for inv in invoices:
        employees.add(inv.contract.employee)
        states.add(inv.contract.employee.state)
    report = []
    for state in states:
        state_obj = {'state': state.name, 'employees': []}
        report.append(state_obj)
        for employee in employees:
            if employee.state == state:
                employee_name = '%s %s' % (employee.firstname, employee.lastname)
                regular = 0.0
                overtime = 0.0
                doubletime = 0.0
                for inv in invoices:
                   if inv.contract.employee == employee:
                       for item in session.query(Iitem).filter(Iitem.invoice_id == inv.id):
                           if item.description == 'Regular':
                               regular += item.cost * item.quantity
                           if item.description == 'Overtime':
                               overtime += item.cost * item.quantity
                           if item.description == 'Doubletime':
                               doubletime += item.cost * item.quantity
                state_obj['employees'].append({
                    'employee': employee_name,
                    'regular': regular,
                    'overtime': overtime,
                    'doubletime': doubletime,
                })

    return report
