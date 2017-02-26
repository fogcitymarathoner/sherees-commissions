import os

from flask_script import Manager
from flask import Flask
from tabulate import tabulate

from keyczar import keyczar
from rrg.models import session_maker
from rrg.contracts import selection_list_active as selection_list

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
def contracts_active():
    session = session_maker(
        app.config['MYSQL_USER'], app.config['MYSQL_PASS'], app.config['MYSQL_SERVER_PORT_3306_TCP_ADDR'],
        app.config['MYSQL_SERVER_PORT_3306_TCP_PORT'], app.config['DB'])
    crypter = keyczar.Crypter.Read(app.config['KEYZCAR_DIR'])

    print(
    tabulate(
        selection_list(session, crypter),
        headers=['number', 'sqlid', 'contract', 'employee', 'startdate', 'enddate']))


if __name__ == "__main__":
    manager.run()
