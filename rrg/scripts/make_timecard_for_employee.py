import os
from datetime import datetime as dt
from datetime import timedelta as td
from flask_script import Manager
from flask import Flask
from tabulate import tabulate
from keyczar import keyczar

from rrg.employees import selection_list_active as selection_list
from rrg.models import Contract
from rrg.models import Employee
from rrg.models import session_maker

from rrg.reminders import weeks_between_dates
from rrg.reminders import biweeks_between_dates
from rrg.reminders import semimonths_between_dates
from rrg.reminders import months_between_dates
from rrg.reminders_generation import create_invoice_for_period
from s3_mysql_backup import YMD_FORMAT

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
    session = session_maker(
        app.config['MYSQL_USER'], app.config['MYSQL_PASS'], app.config['MYSQL_SERVER_PORT_3306_TCP_ADDR'],
        app.config['MYSQL_SERVER_PORT_3306_TCP_PORT'], app.config['DB'])
    crypter = keyczar.Crypter.Read(app.config['KEYZCAR_DIR'])
    employee_list = selection_list(session, crypter)
    print(
        tabulate(
            employee_list, headers=[
                'number', 'sqlid', 'employee', 'ssn', 'bankaccountnumber', 'bankroutingnumber']))
    selection = raw_input("Please select an employee or 'q' to quit: ")
    if selection == 'q':
        quit()
    selected_employee = employee_list[int(selection)-1]

    employee = session.query(Employee).get(int(selected_employee[1]))
    print '%s %s' % (employee.firstname, employee.lastname)
    contracts = []
    for i, c in enumerate(employee.contracts):
        if c.active:
            contracts.append([i + 1, c.id, c.client.name, c.startdate, c.enddate])
    print tabulate(contracts, headers=['number', 'sqlid', 'client', 'title', 'startdate', 'enddate'])
    selection = raw_input("Please select an employee's contract or 'q' to quit: ")
    if selection == 'q':
        quit()
    selected_contract = contracts[int(selection) - 1]
    print selected_contract
    contract = session.query(Contract).get(int(selected_contract[1]))
    print contract.period_id
    periods = []
    if contract.period_id == 1:
        for i, p in enumerate(weeks_between_dates(dt.now() - td(days=90), dt.now())):
            periods.append([i + 1, dt.strftime(p[0], YMD_FORMAT), dt.strftime(p[1], YMD_FORMAT)])
    print tabulate(periods, headers=['number', 'period start', 'period end'])
    selection = raw_input("Please select a period for timecard or 'q' to quit: ")
    if selection == 'q':
        quit()
    selected_period = periods[int(selection) - 1]
    new_inv = create_invoice_for_period(session, contract, selected_period[1], selected_period[2])
    new_inv.voided = False
    new_inv.mock = False
    new_inv.timecard = True
    session.commit()

if __name__ == "__main__":
    manager.run()
