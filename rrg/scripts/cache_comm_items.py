import os
import argparse

from flask_script import Manager
from flask import Flask
from rrg.sherees_commissions import cache_comm_items as cache_commissions_items
from rrg.models_api import session_maker

parser = argparse.ArgumentParser(description='RRG Cache Commissions Items')

parser.add_argument('project', help='project name', choices=['rrg', 'biz'])
parser.add_argument(
    '--datadir', required=True,
    help='datadir dir with commissions items',
    default='/php-apps/cake.rocketsredglare.com/rrg/data/')

parser.add_argument('--db-user', required=True, help='database user', default='marcdba')
parser.add_argument('--mysql-host', required=True, help='database host - MYSQL_PORT_3306_TCP_ADDR', default='marcdba')
parser.add_argument('--mysql-port', required=True, help='database port - MYSQL_PORT_3306_TCP_PORT', default=3306)
parser.add_argument('--db', required=True, help='d', default='rrg')
parser.add_argument('--db-pass', required=True, help='database pw', default='deadbeef')

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


def cache_comm_items_ep():
    """
    replaces cake cache commissions items
    """
    args = parser.parse_args()

    session = session_maker(args.db_user, args.db_pass, args.mysql_host, args.mysql_port, args.db)
    if args.project == 'rrg':
        print('Caching Commission Items into %s' % os.path.join(args.datadir, 'transactions', 'invoices', 'invoice_items', 'commissions_items'))
        cache_commissions_items(session, args.datadir)
    else:
        print('Project not "rrg" skipping Caching Commission Items')


manager = Manager(app)


@manager.command
def cache_comm_items():
    session = session_maker(
        app.config['MYSQL_USER'], app.config['MYSQL_PASS'], app.config['MYSQL_SERVER_PORT_3306_TCP_ADDR'],
        app.config['MYSQL_SERVER_PORT_3306_TCP_PORT'], app.config['DB'])
    print(
        'Caching Commission Items into %s' % os.path.join(
            app.config['DATADIR'], 'transactions', 'invoices', 'invoice_items', 'commissions_items'))
    cache_commissions_items(session, app.config['DATADIR'])


if __name__ == "__main__":
    manager.run()

