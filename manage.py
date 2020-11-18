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
def exp2018():
    total1 = 0.0
    exps1 = lib.list_year_expenses(year=2018, category=1)
    for exp in exps1:
        print('%s %s %s %s' % (exp['category'], exp['id'], exp['date'], exp['amount']))
        total1 += exp['amount']
    print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
    print('Total %s' % total1)
    total2 = 0.0
    exps2 = lib.list_year_expenses(year=2018, category=2)
    for exp in exps2:
        print('%s %s %s %s' % (exp['category'], exp['id'], exp['date'], exp['amount']))
        total2 += exp['amount']
    print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
    print('Total %s' % total2)
    total3 = 0.0
    exps3 = lib.list_year_expenses(year=2018, category=3)
    for exp in exps3:
        print('%s %s %s %s' % (exp['category'], exp['id'], exp['date'], exp['amount']))
        total3 += exp['amount']
    print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
    print('Total %s' % total3)
    total4 = 0.0
    exps4 = lib.list_year_expenses(year=2018, category=4)
    for exp in exps4:
        print('%s %s %s %s' % (exp['category'], exp['id'], exp['date'], exp['amount']))
        total4 += exp['amount']
    print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
    print('Total %s' % total4)
    total5 = 0.0
    exps5 = lib.list_year_expenses(year=2018, category=5)
    for exp in exps5:
        print('%s %s %s %s' % (exp['category'], exp['id'], exp['date'], exp['amount']))
        total5 += exp['amount']
    print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
    print('Total %s' % total5)
    total6 = 0.0
    exps6 = lib.list_year_expenses(year=2018, category=6)
    for exp in exps6:
        print('%s %s %s %s' % (exp['category'], exp['id'], exp['date'], exp['amount']))
        total6 += exp['amount']
    print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
    print('Total %s' % total6)
    total7 = 0.0
    exps7 = lib.list_year_expenses(year=2018, category=7)
    for exp in exps7:
        print('%s %s %s %s' % (exp['category'], exp['id'], exp['date'], exp['amount']))
        total7 += exp['amount']
    print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
    print('Total %s' % total7)
    total8 = 0.0
    exps8 = lib.list_year_expenses(year=2018, category=8)
    for exp in exps8:
        print('%s %s %s %s' % (exp['category'], exp['id'], exp['date'], exp['amount']))
        total8 += exp['amount']
    print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
    print('Total %s' % total8)
    total9 = 0.0
    exps9 = lib.list_year_expenses(year=2018, category=9)
    for exp in exps9:
        print('%s %s %s %s' % (exp['category'], exp['id'], exp['date'], exp['amount']))
        total9 += exp['amount']
    print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
    print('Total %s' % total9)
    total10 = 0.0
    exps10 = lib.list_year_expenses(year=2018, category=10)
    for exp in exps10:
        print('%s %s %s %s' % (exp['category'], exp['id'], exp['date'], exp['amount']))
        total10 += exp['amount']
    print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
    print('Total %s' % total10)
    total11 = 0.0
    exps11 = lib.list_year_expenses(year=2018, category=11)
    for exp in exps11:
        print('%s %s %s %s' % (exp['category'], exp['id'], exp['date'], exp['amount']))
        total11 += exp['amount']
    print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
    print('Total %s' % total11)
    total12 = 0.0
    exps12 = lib.list_year_expenses(year=2018, category=12)
    for exp in exps12:
        print('%s %s %s %s' % (exp['category'], exp['id'], exp['date'], exp['amount']))
        total12 += exp['amount']
    print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
    print('Total %s' % total12)

@manager.command
def jmp_invoices():
    """"""
    print('JMP Invoice')
    contract = session.query(models.Contract).get(1479)
    _invoices_report(contract)

if __name__ == "__main__":
    manager.run()
