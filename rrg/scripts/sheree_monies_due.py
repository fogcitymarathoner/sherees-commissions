import os
import argparse
from flask_script import Manager
from flask import Flask
from rrg.sherees_commissions import comm_latex_document_header
from rrg.commissions import employee_total_monies_owed
from rrg.models import session_maker
from rrg.sherees_commissions import sa_sheree

parser = argparse.ArgumentParser(description='RRG Money Due to Sheree Summary Report')

parser.add_argument('--format', required=True, choices=['plain', 'latex'], help='output format', default='plain')

parser.add_argument(
    '--datadir',
    required=True,
    help='datadir dir with ar.xml',
    default='/php-apps/cake.rocketsredglare.com/rrg/data/transactions/invoices/invoice_items/commissions_items/')

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


def monies_due_ep():
    args = parser.parse_args()
    session = session_maker(args.db_user, args.db_pass, args.mysql_host, args.mysql_port, args.db)
    if args.format == 'plain':
        print(employee_total_monies_owed(session, sa_sheree(session), args.datadir, args.cache, format))
    elif args.format == 'latex':
        report = comm_latex_document_header("Sheree's Monies Due Report")
        report += employee_total_monies_owed(session, sa_sheree(session), args.datadir, args.cache, format)
        report += '\n\end{document}\n'
        print(report)


manager = Manager(app)


@manager.option('-c', '--cache', dest='cache', default=True)
@manager.option('-f', '--format', help='type of output plain or latex', required=True, choices=['plain', 'latex'])
def monies_due(format, cache):
    session = session_maker(
        app.config['MYSQL_USER'], app.config['MYSQL_PASS'], app.config['MYSQL_SERVER_PORT_3306_TCP_ADDR'],
        app.config['MYSQL_SERVER_PORT_3306_TCP_PORT'], app.config['DB'])
    if args.format == 'plain':
        print(employee_total_monies_owed(session, sa_sheree(session), app.config['DATADIR'], cache, format))
    elif format == 'latex':
        report = comm_latex_document_header("Sheree's Monies Due Report")
        report += employee_total_monies_owed(session, sa_sheree(session), app.config['DATADIR'], cache, format)
        report += '\n\end{document}\n'
        print(report)


if __name__ == "__main__":
    manager.run()
