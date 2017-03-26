import os
import argparse
from flask_script import Manager
from flask import Flask
from rrg.sherees_commissions import sherees_notes_report_db
from rrg.sherees_commissions import comm_latex_document_header
from rrg.models_api import session_maker

parser = argparse.ArgumentParser(description='RRG Sherees Notes Report From DB')

parser.add_argument('--format', required=True, choices=['plain', 'latex'], help='output format')

parser.add_argument('--db-user', required=True, help='database user', default='marcdba')
parser.add_argument('--mysql-host', required=True, help='database host - MYSQL_PORT_3306_TCP_ADDR', default='marcdba')
parser.add_argument('--mysql-port', required=True, help='database port - MYSQL_PORT_3306_TCP_PORT', default=3306)
parser.add_argument('--db', required=True, help='d', default='rrg')
parser.add_argument('--db-pass', required=True, help='database pw', default='deadbeef')

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


def notes_ep():
    """
    print notes report as a document
    :return:
    """
    args = parser.parse_args()

    session = session_maker(args.db_user, args.db_pass, args.mysql_host, args.mysql_port, args.db)
    if args.format == 'plain':
        print(sherees_notes_report_db(session, args.format))
    elif args.format == 'latex':
        report = comm_latex_document_header("Sheree's Notes Report")
        report += sherees_notes_report_db(session, args.format)
        report += '\n\end{document}\n'
        print(report)


manager = Manager(app)


@manager.option(
    '-f', '--format', help='format of commissions report - plain, latex', choices=['plain', 'latex'], default='plain')
def notes():
    session = session_maker(
        app.config['MYSQL_USER'], app.config['MYSQL_PASS'], app.config['MYSQL_SERVER_PORT_3306_TCP_ADDR'],
        app.config['MYSQL_SERVER_PORT_3306_TCP_PORT'], app.config['DB'])
    if format == 'plain':
        print(sherees_notes_report_db(session, format))
    elif format == 'latex':
        report = comm_latex_document_header("Sheree's Notes Report")
        report += sherees_notes_report_db(session, format)
        report += '\n\end{document}\n'
        print(report)


if __name__ == "__main__":
    manager.run()
