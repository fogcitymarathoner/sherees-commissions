
import os

from flask import Flask
from flask_script import Manager

import rrg.xml_helpers


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


@manager.command
def assemble_contracts_cache():
    print('Assembling Contracts in %s' % os.path.join(app.config['DATADIR'], 'contracts'))
    rrg.xml_helpers.cached_contracts_collect_invoices_and_items(app.config['DATADIR'])

if __name__ == "__main__":
    manager.run()

