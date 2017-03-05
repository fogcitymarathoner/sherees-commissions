import os
from datetime import datetime as dt
from datetime import timedelta as td

from flask import Flask
from flask_script import Manager
from s3_mysql_backup import YMD_FORMAT
from tabulate import tabulate

from rrg import utils
from rrg.billing import cache_non_date_parsed
from rrg.lib import archive
from rrg.lib import reminders
from rrg.lib import reminders_generation
from rrg.models import Contract
from rrg.models import Employee
from rrg.models import EmployeeMemo
from rrg.models import EmployeePayment
from rrg.models import edit_employee_script
from rrg.models import session_maker
from rrg.models import employees
from rrg.renderers import format_employee

app = Flask(__name__, instance_relative_config=True)

# Load the default configuration
if os.environ.get('RRG_SETTINGS'):
    settings_file = os.environ.get('RRG_SETTINGS')
else:
    print('Environment Variable RRG_SETTINGS not set')
    quit(1)

if os.path.isfile(settings_file):
    try:
        app.config.from_envvar('RRG_SETTINGS')
    except Exception as e:
        print('something went wrong with config file %s' % settings_file)
        quit(1)
else:
    print('settings file %s does not exits' % settings_file)


manager = Manager(app)


@manager.command
def make_timecard_for_employee():
    """
    A Text-based user workflow to make a time card for an employee
    # select active employee
    # select active contract of selected employee
    # select any period going 90 days back
    Goes back 90 days
    :return:
    """
    session = session_maker(
        app.config['MYSQL_USER'], app.config['MYSQL_PASS'], app.config['MYSQL_SERVER_PORT_3306_TCP_ADDR'],
        app.config['MYSQL_SERVER_PORT_3306_TCP_PORT'], app.config['DB'])
    employee_list = employees.selection_list_active(session)
    #
    # Select an Active Employee
    print(
        tabulate(
            employee_list, headers=[
                'number', 'sqlid', 'employee', 'ssn', 'bankaccountnumber', 'bankroutingnumber']))
    selection = input("Please select an employee or 'q' to quit: ")
    if selection == 'q':
        quit()
    selected_employee = employee_list[int(selection)-1]

    employee = session.query(Employee).get(int(selected_employee[1]))
    print('%s %s' % (employee.firstname, employee.lastname))
    #
    # Select an Active Contract of the Employee's
    contracts = []
    for i, c in enumerate(employee.contracts):
        if c.active:
            contracts.append([i + 1, c.id, c.client.name, c.startdate, c.enddate])
    print(tabulate(contracts, headers=['number', 'sqlid', 'client', 'title', 'startdate', 'enddate']))
    selection = input("Please select an employee's contract or 'q' to quit: ")
    if selection == 'q':
        quit()
    selected_contract = contracts[int(selection) - 1]
    contract = session.query(Contract).get(int(selected_contract[1]))
    # Weekly Contract
    if contract.period_id == 1:
        periods_for_contract = reminders.weeks_between_dates(dt.now() - td(days=90), dt.now())
    # Bi-Weekly Contract
    elif contract.period_id == 2:
        periods_for_contract = reminders.biweeks_between_dates(dt.now() - td(days=90), dt.now())
    # Semi-Monthly Contract
    elif contract.period_id == 3:
        periods_for_contract = reminders.semimonths_between_dates(dt.now() - td(days=90), dt.now())
    # Monthly Contract
    elif contract.period_id == 4:
        periods_for_contract = reminders.months_between_dates(dt.now() - td(days=90), dt.now())
    # Tabulate the periods for selection
    periods = []
    for i, p in enumerate(periods_for_contract):
        periods.append([i + 1, dt.strftime(p[0], YMD_FORMAT), dt.strftime(p[1], YMD_FORMAT)])
    print(tabulate(periods, headers=['number', 'period start', 'period end']))
    selection = input("Please select a period for timecard or 'q' to quit: ")
    if selection == 'q':
        quit()
    selected_period = periods[int(selection) - 1]
    new_inv = reminders_generation.create_invoice_for_period(session, contract, selected_period[1], selected_period[2])
    new_inv.voided = False
    new_inv.mock = False
    new_inv.timecard = True
    session.commit()


@manager.option('-n', '--number', dest='number', required=True)
def edit_employee(number):
    session = session_maker(
        app.config['MYSQL_USER'], app.config['MYSQL_PASS'], app.config['MYSQL_SERVER_PORT_3306_TCP_ADDR'],
        app.config['MYSQL_SERVER_PORT_3306_TCP_PORT'], app.config['DB'])

    edit_employee_script(session, int(number))
    session.commit()


@manager.command
def cached_employees():

    print('Archived Employees in %s' % app.config['DATADIR'])
    employees(app.config['DATADIR'])


@manager.option('-i', '--id', dest='id', required=True)
def cached_employee(id):

    print('Archived Employee in %s' % app.config['DATADIR'])
    employee_dict = archive.employee(id, app.config['DATADIR'])

    print(format_employee(employee_dict))


@manager.command
def cache_employee_memos():
    session = session_maker(
        app.config['MYSQL_USER'], app.config['MYSQL_PASS'], app.config['MYSQL_SERVER_PORT_3306_TCP_ADDR'],
        app.config['MYSQL_SERVER_PORT_3306_TCP_PORT'], app.config['DB'])
    print('Caching Employees-Memos %s into %s' % (app.config['DB'], utils.employees_memos_dir(app.config['DATADIR'])))
    cache_non_date_parsed(session, utils.employees_memos_dir(app.config['DATADIR']), EmployeeMemo)
    session.commit()


@manager.command
def cache_employees():
    session = session_maker(
        app.config['MYSQL_USER'], app.config['MYSQL_PASS'], app.config['MYSQL_SERVER_PORT_3306_TCP_ADDR'],
        app.config['MYSQL_SERVER_PORT_3306_TCP_PORT'], app.config['DB'])
    print('Caching Employees %s into %s' % (app.config['DB'], os.path.join(app.config['DATADIR'], 'employees')))
    cache_non_date_parsed(session, os.path.join(app.config['DATADIR'], 'employees'), Employee)
    session.commit()


@manager.command
def cache_employees_payments():
    session = session_maker(
        app.config['MYSQL_USER'], app.config['MYSQL_PASS'], app.config['MYSQL_SERVER_PORT_3306_TCP_ADDR'],
        app.config['MYSQL_SERVER_PORT_3306_TCP_PORT'], app.config['DB'])
    
    print(
        'Caching Employees-Payments %s into %s' % (
            app.config['DB'], os.path.join(app.config['DATADIR'], 'employees', 'payments')))
    cache_non_date_parsed(session, os.path.join(app.config['DATADIR'], 'employees', 'payments'), EmployeePayment)
    session.commit()

@manager.command
def assemble_employees_cache():
    """
    Assembles Employees related data into a big comprehensive documents
    :return:
    """
    print('Assembling Employees in %s' % os.path.join(app.config['DATADIR'], 'employees'))
    archive.cached_employees_collect_contracts(app.config['DATADIR'])


@manager.command
def list_all_employees():
    """
    Return a list of enumerated all employees
    :return:
    """
    session = session_maker(
        app.config['MYSQL_USER'], app.config['MYSQL_PASS'], app.config['MYSQL_SERVER_PORT_3306_TCP_ADDR'],
        app.config['MYSQL_SERVER_PORT_3306_TCP_PORT'], app.config['DB'])

    print(
        tabulate(
            employees.selection_list_all(session),
            headers=['number', 'sqlid', 'employee', 'ssn', 'bankaccountnumber', 'bankroutingnumber']))


@manager.command
def list_active_employees():
    """
    Return a list of enumerated active employees
    :return:
    """
    session = session_maker(
        app.config['MYSQL_USER'], app.config['MYSQL_PASS'], app.config['MYSQL_SERVER_PORT_3306_TCP_ADDR'],
        app.config['MYSQL_SERVER_PORT_3306_TCP_PORT'], app.config['DB'])

    print(
        tabulate(
            employees.selection_list_active(session),
            headers=['number', 'sqlid', 'employee', 'ssn', 'bankaccountnumber', 'bankroutingnumber']))


@manager.command
def list_inactive_employees():
    """
    Return a list of enumerated inactive employees
    :return:
    """
    session = session_maker(
        app.config['MYSQL_USER'], app.config['MYSQL_PASS'], app.config['MYSQL_SERVER_PORT_3306_TCP_ADDR'],
        app.config['MYSQL_SERVER_PORT_3306_TCP_PORT'], app.config['DB'])

    print(
        tabulate(
            employees.selection_list_inactive(session),
            headers=['number', 'sqlid', 'employee', 'ssn', 'bankaccountnumber', 'bankroutingnumber']))


if __name__ == "__main__":
    manager.run()
