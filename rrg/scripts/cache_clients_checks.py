import os
import argparse

from flask_script import Manager
from flask import Flask
from rrg.billing import cache_non_date_parsed as routine
from rrg.models import ClientCheck
from rrg.models_api import session_maker

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


def cache_checks_ep():
    """
    replaces cake cache clients checks
    """
    args = parser.parse_args()
    session = session_maker(args.db_user, args.db_pass, args.mysql_host, args.mysql_port, args.db)
    print('Caching Clients-Checks %s into %s' % (args.db, os.path.join(args.datadir, 'transactions', 'checks')))
    routine(session, os.path.join(args.datadir, 'transactions', 'checks'), ClientCheck)
    session.commit()


manager = Manager(app)


@manager.command
def cache_checks():
    session = session_maker(
        app.config['MYSQL_USER'], app.config['MYSQL_PASS'], app.config['MYSQL_SERVER_PORT_3306_TCP_ADDR'],
        app.config['MYSQL_SERVER_PORT_3306_TCP_PORT'], app.config['DB'])
    print(
        'Caching Clients-Checks %s into %s' % (
            app.config['DATADIR'], os.path.join(app.config['DATADIR'], 'transactions', 'checks')))
    routine(session, os.path.join(app.config['DATADIR'], 'transactions', 'checks'), ClientCheck)
    session.commit()


if __name__ == "__main__":
    manager.run()
