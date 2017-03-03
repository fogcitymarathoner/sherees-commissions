import os
from flask_script import Manager
from flask import Flask

from rrg.models import pastdue_invoices as sa_pastdue_invoices
from rrg.models import session_maker
from rrg.models import tabulate_invoices


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
    '-f', '--format', help='format of commissions report - plain, latex', choices=['plain', 'latex'], default='plain')
def pastdue_invoices(format):
    session = session_maker(
        app.config['MYSQL_USER'], app.config['MYSQL_PASS'], app.config['MYSQL_SERVER_PORT_3306_TCP_ADDR'],
        app.config['MYSQL_SERVER_PORT_3306_TCP_PORT'], app.config['DB'])
    w_pastdue_invoices = sa_pastdue_invoices(session)

    print(tabulate_invoices(w_pastdue_invoices))


if __name__ == "__main__":
    manager.run()

