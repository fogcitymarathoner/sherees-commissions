#!
import os

from flask import Flask
from flask_script import Manager

from rrg.models import generate_ar_report

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


@manager.option(
    '-t',
    '--type', required=True,
    help='type of ar report - all, open, pastdue, cleared', choices=['all', 'open', 'pastdue', 'cleared'])
def ar_report(type):
    """
    generates ar reports open, pastdue, and all
    requires
    cache.py client_accounts_receivable
    invoices.py cache_invoice
    :param type:
    :return:
    """
    print generate_ar_report(app, type)

if __name__ == "__main__":
    manager.run()