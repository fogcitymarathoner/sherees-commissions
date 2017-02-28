import os

from flask_script import Manager
from flask import Flask
from tabulate import tabulate

from keyczar import keyczar

from rrg.archive import cached_employees_collect_contracts
from rrg.archive import employee
from rrg.archive import employees
from rrg.billing import cache_non_date_parsed
from rrg.models import session_maker
from rrg.models import Employee
from rrg.employees import selection_list_all
from rrg.employees import selection_list_active
from rrg.employees import selection_list_inactive
from rrg.models import EmployeeMemo
from rrg.models import EmployeePayment
from rrg.renderers import format_employee
from rrg.utils import edit_employee as utils_edit_employee
from rrg.utils import employees_memos_dir

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


@manager.option('-n', '--number', dest='number', required=True)
def edit_employee(number):
    session = session_maker(
        app.config['MYSQL_USER'], app.config['MYSQL_PASS'], app.config['MYSQL_SERVER_PORT_3306_TCP_ADDR'],
        app.config['MYSQL_SERVER_PORT_3306_TCP_PORT'], app.config['DB'])
    crypter = keyczar.Crypter.Read(app.config['KEYZCAR_DIR'])

    utils_edit_employee(session, crypter, int(number))
    session.commit()


@manager.command
def cached_employees():

    print('Archived Employees in %s' % app.config['DATADIR'])
    employees(app.config['DATADIR'])


@manager.option('-i', '--id', dest='id', required=True)
def cached_employee(id):

    print('Archived Employee in %s' % app.config['DATADIR'])
    employee_dict = employee(id, app.config['DATADIR'])

    print format_employee(employee_dict)


@manager.command
def cache_employee_memos():
    session = session_maker(
        app.config['MYSQL_USER'], app.config['MYSQL_PASS'], app.config['MYSQL_SERVER_PORT_3306_TCP_ADDR'],
        app.config['MYSQL_SERVER_PORT_3306_TCP_PORT'], app.config['DB'])
    crypter = keyczar.Crypter.Read(app.config['KEYZCAR_DIR'])
    print('Caching Employees-Memos %s into %s' % (app.config['DB'], employees_memos_dir(app.config['DATADIR'])))
    cache_non_date_parsed(session, employees_memos_dir(app.config['DATADIR']), EmployeeMemo, crypter)
    session.commit()


@manager.command
def cache_employees():
    session = session_maker(
        app.config['MYSQL_USER'], app.config['MYSQL_PASS'], app.config['MYSQL_SERVER_PORT_3306_TCP_ADDR'],
        app.config['MYSQL_SERVER_PORT_3306_TCP_PORT'], app.config['DB'])
    crypter = keyczar.Crypter.Read(app.config['KEYZCAR_DIR'])
    print('Caching Employees %s into %s' % (app.config['DB'], os.path.join(app.config['DATADIR'], 'employees')))
    cache_non_date_parsed(session, os.path.join(app.config['DATADIR'], 'employees'), Employee, crypter)
    session.commit()


@manager.command
def cache_employees_payments():
    session = session_maker(
        app.config['MYSQL_USER'], app.config['MYSQL_PASS'], app.config['MYSQL_SERVER_PORT_3306_TCP_ADDR'],
        app.config['MYSQL_SERVER_PORT_3306_TCP_PORT'], app.config['DB'])
    crypter = keyczar.Crypter.Read(app.config['KEYZCAR_DIR'])
    print(
        'Caching Employees-Payments %s into %s' % (
            app.config['DB'], os.path.join(app.config['DATADIR'], 'employees', 'payments')))
    cache_non_date_parsed(session, os.path.join(app.config['DATADIR'], 'employees', 'payments'), EmployeePayment, crypter)
    session.commit()

@manager.command
def assemble_employees_cache():
    """
    Assembles Employees related data into a big comprehensive documents
    :return:
    """
    print('Assembling Employees in %s' % os.path.join(app.config['DATADIR'], 'employees'))
    cached_employees_collect_contracts(app.config['DATADIR'])


@manager.command
def list_all_employees():
    """
    Return a list of enumerated all employees
    :return:
    """
    session = session_maker(
        app.config['MYSQL_USER'], app.config['MYSQL_PASS'], app.config['MYSQL_SERVER_PORT_3306_TCP_ADDR'],
        app.config['MYSQL_SERVER_PORT_3306_TCP_PORT'], app.config['DB'])
    crypter = keyczar.Crypter.Read(app.config['KEYZCAR_DIR'])

    print(
        tabulate(
            selection_list_all(session, crypter),
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
    crypter = keyczar.Crypter.Read(app.config['KEYZCAR_DIR'])

    print(
        tabulate(
            selection_list_active(session, crypter),
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
    crypter = keyczar.Crypter.Read(app.config['KEYZCAR_DIR'])

    print(
        tabulate(
            selection_list_inactive(session, crypter),
            headers=['number', 'sqlid', 'employee', 'ssn', 'bankaccountnumber', 'bankroutingnumber']))


if __name__ == "__main__":
    manager.run()
