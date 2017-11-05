import datetime as dt

from flask_alembic import alembic_script
from flask_script import Manager

from app import app
import lib
from rrg import models

from app import session

manager = Manager(app)

manager.add_command('db', alembic_script)

@manager.command
def past_due_invoices():
    """Print past due invoices"""

    for inv in lib.pastdue_invoices():
        print('%s %s %s' % (inv['id'], inv['date'], inv['contract']['client']['name']))

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


if __name__ == "__main__":
    manager.run()
