import os

from flask_script import Manager
from flask import Flask
from rrg import utils
from rrg.billing import cache_non_date_parsed
from rrg.models import session_maker
from rrg.models import Client
from rrg.models import ClientMemo
from rrg.models import ClientManager
from rrg.models import Contract
from rrg.models import Employee
from rrg.models import Invoice
from rrg.models import State
from rrg.models import cache_objs
from rrg.models import clients_ar_xml_file

from rrg.utils import clients_memos_dir
from rrg.utils import clients_managers_dir
from rrg import cache_clients_ar

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
def clients():
    session = session_maker(
        app.config['MYSQL_USER'], app.config['MYSQL_PASS'], app.config['MYSQL_SERVER_PORT_3306_TCP_ADDR'],
        app.config['MYSQL_SERVER_PORT_3306_TCP_PORT'], app.config['DB'])
    print('Caching Clients %s into %s' % (app.config['DB'], os.path.join(app.config['DATADIR'], 'clients')))
    cache_non_date_parsed(session, os.path.join(app.config['DATADIR'], 'clients'), Client)
    session.commit()


@manager.command
def client_memos():
    session = session_maker(
        app.config['MYSQL_USER'], app.config['MYSQL_PASS'], app.config['MYSQL_SERVER_PORT_3306_TCP_ADDR'],
        app.config['MYSQL_SERVER_PORT_3306_TCP_PORT'], app.config['DB'])
    print('Caching Clients-Memos %s into %s' % (app.config['DB'], clients_memos_dir(app.config['DATADIR'])))
    cache_non_date_parsed(session, clients_memos_dir(app.config['DATADIR']), ClientMemo)
    session.commit()


@manager.command
def client_managers():
    session = session_maker(
        app.config['MYSQL_USER'], app.config['MYSQL_PASS'], app.config['MYSQL_SERVER_PORT_3306_TCP_ADDR'],
        app.config['MYSQL_SERVER_PORT_3306_TCP_PORT'], app.config['DB'])
    print('Caching Clients-Managers %s into %s' % (app.config['DB'], clients_managers_dir(app.config['DATADIR'])))
    cache_non_date_parsed(session, clients_managers_dir(app.config['DATADIR']), ClientManager)
    session.commit()


@manager.command
def invoices():
    """
    cache xml invoices
    :return:
    """
    session = session_maker(
        app.config['MYSQL_USER'], app.config['MYSQL_PASS'], app.config['MYSQL_SERVER_PORT_3306_TCP_ADDR'],
        app.config['MYSQL_SERVER_PORT_3306_TCP_PORT'], app.config['DB'])

    print(
        'Caching Invoices %s into %s' % (
            app.config['DB'], os.path.join(app.config['DATADIR'], 'transactions', 'invoices')))
    cache_non_date_parsed(session, os.path.join(app.config['DATADIR'], 'transactions', 'invoices'), Invoice)
    session.commit()


@manager.command
def client_accounts_receivable():
    session = session_maker(
        app.config['MYSQL_USER'], app.config['MYSQL_PASS'], app.config['MYSQL_SERVER_PORT_3306_TCP_ADDR'],
        app.config['MYSQL_SERVER_PORT_3306_TCP_PORT'], app.config['DB'])
    print('Caching Clients AR into %s' % clients_ar_xml_file(app.config['DATADIR']))
    cache_clients_ar(session, app.config['DATADIR'])


@manager.command
def contracts():
    session = session_maker(
        app.config['MYSQL_USER'], app.config['MYSQL_PASS'], app.config['MYSQL_SERVER_PORT_3306_TCP_ADDR'],
        app.config['MYSQL_SERVER_PORT_3306_TCP_PORT'], app.config['DB'])

    print('Caching Contracts %s into %s' % (app.config['DB'], os.path.join(app.config['DATADIR'], 'contracts')))
    cache_non_date_parsed(session, os.path.join(app.config['DATADIR'], 'contracts'), Contract)
    session.commit()


@manager.command
def states():
    session = session_maker(
        app.config['MYSQL_USER'], app.config['MYSQL_PASS'], app.config['MYSQL_SERVER_PORT_3306_TCP_ADDR'],
        app.config['MYSQL_SERVER_PORT_3306_TCP_PORT'], app.config['DB'])

    print('Caching States %s into %s' % (app.config['DB'], os.path.join(app.config['DATADIR'], 'states')))
    states = session.query(State).all()
    cache_objs(app.config['DATADIR'], states)
    session.commit()


@manager.command
def employees():
    session = session_maker(
        app.config['MYSQL_USER'], app.config['MYSQL_PASS'], app.config['MYSQL_SERVER_PORT_3306_TCP_ADDR'],
        app.config['MYSQL_SERVER_PORT_3306_TCP_PORT'], app.config['DB'])

    print('Caching States %s into %s' % (app.config['DB'], os.path.join(app.config['DATADIR'], 'states')))
    employees = session.query(Employee).all()
    cache_objs(app.config['DATADIR'], employees)
    session.commit()


@manager.command
def contract_items():
    session = session_maker(
        app.config['MYSQL_USER'], app.config['MYSQL_PASS'], app.config['MYSQL_SERVER_PORT_3306_TCP_ADDR'],
        app.config['MYSQL_SERVER_PORT_3306_TCP_PORT'], app.config['DB'])
    print(
        'Caching Contract Items %s into %s' % (
            app.config['DB'], os.path.join(app.config['DATADIR'], 'contracts', 'contract_items')))
    cache_non_date_parsed(session, os.path.join(app.config['DATADIR'], 'contracts', 'contract_items'), ContractItem)
    session.commit()

if __name__ == "__main__":
    manager.run()
