import os
import argparse
from flask_script import Manager
from flask import Flask

from rrg.models_api import open_invoices as sa_open_invoices, tabulate_invoices, session_maker
from rrg.models import session_maker
from rrg.models import tabulate_invoices

parser = argparse.ArgumentParser(description='RRG Open Invoices')

parser.add_argument('--db-user', required=True, help='database user',
                    default='marcdba')
parser.add_argument('--mysql-host', required=True,
                    help='database host - MYSQL_PORT_3306_TCP_ADDR',
                    default='marcdba')
parser.add_argument('--mysql-port', required=True,
                    help='database port - MYSQL_PORT_3306_TCP_PORT',
                    default=3306)
parser.add_argument('--db', required=True, help='d', default='rrg')
parser.add_argument('--db-pass', required=True, help='database pw',
                    default='deadbeef')

app = Flask(__name__, instance_relative_config=True)

# Load the default configuration
if os.environ.get('RRG_SETTINGS'):
    SETTINGS_FILE = os.environ.get('RRG_SETTINGS')
else:
    print('Environment Variable RRG_SETTINGS not set')
    quit(1)

if os.path.isfile(SETTINGS_FILE):
    try:
        app.config.from_envvar('RRG_SETTINGS')
    except Exception as e:
        print('something went wrong with config file %s' % SETTINGS_FILE)
        quit(1)
else:
    print('settings file %s does not exits' % SETTINGS_FILE)


manager = Manager(app)


@manager.option(
    '-f', '--format', help='format of commissions report - plain, latex', choices=['plain', 'latex'], default='plain')
def open_invoices(format):
    session = session_maker(
        app.config['MYSQL_USER'], app.config['MYSQL_PASS'], app.config['MYSQL_SERVER_PORT_3306_TCP_ADDR'],
        app.config['MYSQL_SERVER_PORT_3306_TCP_PORT'], app.config['DB'])
    w_open_invoices = sa_open_invoices(session)

    print(tabulate_invoices(w_open_invoices))


if __name__ == "__main__":
    manager.run()

