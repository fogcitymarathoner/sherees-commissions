import datetime as dt

from flask_script import Manager

from app import app
import lib
import sheets_lib
from rrg import models

from app import session

manager = Manager(app)

@manager.command
def past_due_invoices():
    """Print past due invoices"""

    for inv in lib.pastdue_invoices():
        print('%s %s %s %s' % (inv['id'], inv['date'], inv['contract']['client']['name'], inv['balance']))

@manager.command
def update_vendors_sheet():
    """Update vendor sheet at google """
    sheets_lib.update_vendors_sheet()

@manager.command
def generate_mileage():
    """Generate fixed mileage entries to be nullified in SQL if false"""

    description = 'IDC-Google 53 miles x 2 @ $.54/mile (2017)'
    contract = session.query(models.Contract).get(1664)
    employee = session.query(models.Employee).get(1479)
    mileage_cat = session.query(models.ExpenseCategory).get(2)
    startdate = dt.datetime(year=contract.startdate.year, month=contract.startdate.month, day=contract.startdate.day)
    delta = dt.datetime.now() - startdate
    for i in range(delta.days + 1):
        day = startdate + dt.timedelta(days=i)
        if day.weekday() in range(0, 5):
            exp_count = session.query(models.Expense).filter(models.Expense.category == mileage_cat,
                                                             models.Expense.description == description,
                                                             models.Expense.date == day).count()
            if exp_count == 0:
                exp = models.Expense(category=mileage_cat, description=description, amount=53 * 2 * .54, date=day,
                                     employee=employee)
                session.add(exp)
                session.commit()

def _invoices_report(contract):
    invoices = session.query(models.Invoice).filter(models.Invoice.contract == contract, models.Invoice.voided == False).order_by(models.Invoice.period_end.asc())
    for i in invoices:
        print('id: %s, start: %s end: %s amount: %s cleared: %s' % (i.id, i.period_start, i.period_end, i.amount(), i.cleared))

@manager.command
def tobias_invoices():
    """"""
    print('Tobias Invoice')
    contract = session.query(models.Contract).get(2)
    _invoices_report(contract)


@manager.command
def jmp_invoices():
    """"""
    print('JMP Invoice')
    contract = session.query(models.Contract).get(1479)
    _invoices_report(contract)

if __name__ == "__main__":
    manager.run()
