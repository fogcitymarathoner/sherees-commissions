import os
import argparse
from flask_script import Manager
from flask import Flask
from rrg.sherees_commissions import comm_latex_document_header
from rrg.sherees_commissions import sheree_total_monies_owed
from rrg.sherees_commissions import payroll_due_report
from rrg.sherees_commissions import sherees_notes_report_db
from rrg.sherees_commissions import sherees_commissions_report
from rrg.sherees_commissions import inv_report
from rrg.models import session_maker

parser = argparse.ArgumentParser(description='RRG Money Due to Sheree Long Report')

parser.add_argument('--format', required=True, choices=['plain', 'latex'], help='output format', default='plain')
parser.add_argument(
    '--datadir', required=True, help='datadir', default='/php-apps/cake.rocketsredglare.com/rrg/data/')
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


def monies_due():
    args = parser.parse_args()
    session = session_maker(args)
    report = ''
    if args.format == 'plain':
        report += 'Summary\n'
        report += sheree_total_monies_owed(session, args)
        report += '\n'
        report += 'Hourly\n'
        report += payroll_due_report(session, args)
        report += '\n'
        report += 'Notes Report\n'
        report += sherees_notes_report_db(session, args.format)
        report += '\n'
        report += 'Commissions Report\n'
        report += sherees_commissions_report(session, args)
        report += '\n'
        report += 'Invoices Report\n'
        report += inv_report(session, args)
    elif args.format == 'latex':
        report += comm_latex_document_header("Sheree's Monies Due Report")
        report += sheree_total_monies_owed(session, args)
        report += '\n'
        report += payroll_due_report(session, args)
        report += '\n'
        report += sherees_notes_report(session, args)
        report += '\n'
        report += sherees_commissions_report(session, args)
        report += '\n'
        report += inv_report(session, args)
        report += '\n\end{document}\n'
    print(report)
