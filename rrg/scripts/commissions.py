import os

from flask_script import Manager
from flask import Flask
from rrg.commissions import salesperson_commissions_report
from rrg.sherees_commissions import comm_latex_document_header
from rrg.sherees_commissions import sa_sheree
from rrg.models import session_maker

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


@manager.option('-c', '--cache', dest='cache', default=True)
@manager.option(
    '-f', '--format', help='format of commissions report - plain, latex', choices=['plain', 'latex'], default='plain')
def commissions(format, cache):

    session = session_maker(
        app.config['MYSQL_USER'], app.config['MYSQL_PASS'], app.config['MYSQL_SERVER_PORT_3306_TCP_ADDR'],
        app.config['MYSQL_SERVER_PORT_3306_TCP_PORT'], app.config['DB'])
    if format == 'latex':
        report = comm_latex_document_header("Sheree's Commissions")
        report += salesperson_commissions_report(session, sa_sheree(session), cache, app.config['DATADIR'], format)
        report += '\n\end{document}\n'
        print(report)
    else:
        print(salesperson_commissions_report(session, sa_sheree(session), cache, app.config['DATADIR'], format))


if __name__ == "__main__":
    manager.run()
