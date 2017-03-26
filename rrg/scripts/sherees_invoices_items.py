import os
import argparse
from flask_script import Manager
from flask import Flask
from rrg.sherees_commissions import invoices_items as sinvoices_items
from rrg.models_api import session_maker

parser = argparse.ArgumentParser(
    description='RRG Cache Sherees Commissions Invoices Items')

parser.add_argument('project', help='project name', choices=['rrg', 'biz'])

parser.add_argument('--db-user', required=True, help='database user', default='marcdba')
parser.add_argument('--mysql-host', required=True, help='database host - MYSQL_PORT_3306_TCP_ADDR', default='marcdba')
parser.add_argument('--mysql-port', required=True, help='database port - MYSQL_PORT_3306_TCP_PORT', default=3306)
parser.add_argument('--db', required=True, help='d', default='rrg')
parser.add_argument('--db-pass', required=True, help='database pw', default='deadbeef')
parser.add_argument('--cache', dest='cache', action='store_true')
parser.add_argument('--no-cache', dest='cache', action='store_false')
parser.set_defaults(cache=True)

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


def invoices_items_ep():
    """
    replaces cake cache commissions items
    """
    args = parser.parse_args()

    session = session_maker(args.db_user, args.db_pass, args.mysql_host, args.mysql_port, args.db)

    print('Sherees Invoices Items')
    sinvoices_items(session)


manager = Manager(app)


def invoices_items():
    session = session_maker(
        app.config['MYSQL_USER'], app.config['MYSQL_PASS'], app.config['MYSQL_SERVER_PORT_3306_TCP_ADDR'],
        app.config['MYSQL_SERVER_PORT_3306_TCP_PORT'], app.config['DB'])
    print('Sherees Invoices Items')
    sinvoices_items(session)
