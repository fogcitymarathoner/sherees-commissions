import os
import argparse
from tabulate import tabulate

from flask_script import Manager
from flask import Flask
from rrg.reports.invoices import invoices_year_month
from rrg.models import session_maker

parser = argparse.ArgumentParser(description='RRG Invoices Year Month Report')

parser.add_argument('year', type=int, help='commissions year')
parser.add_argument('month', type=int, help='commissions month')

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


def invoices_monthly_ep():
    args = parser.parse_args()

    session = session_maker(args.db_user, args.db_pass, args.mysql_host, args.mysql_port, args.db)
    invs = invoices_year_month(session, args)

    res_dict_transposed = {
        'id': [i.id for i in invs],
        'date': [i.date for i in invs],
        'description': [
            '%s %s-%s' % (i.contract.title, i.period_start, i.period_end) for i
            in invs],
        'amount': [i.amount for i in invs]
    }
    print(tabulate(res_dict_transposed, headers='keys', tablefmt='plain'))


manager = Manager(app)


def invoices_monthly():
    session = session_maker(
        app.config['MYSQL_USER'], app.config['MYSQL_PASS'], app.config['MYSQL_SERVER_PORT_3306_TCP_ADDR'],
        app.config['MYSQL_SERVER_PORT_3306_TCP_PORT'], app.config['DB'])
    invs = invoices_year_month(session, args)

    res_dict_transposed = {
        'id': [i.id for i in invs],
        'date': [i.date for i in invs],
        'description': [
            '%s %s-%s' % (i.contract.title, i.period_start, i.period_end) for i
            in invs],
        'amount': [i.amount for i in invs]
    }
    print(tabulate(res_dict_transposed, headers='keys', tablefmt='plain'))
if __name__ == "__main__":
    manager.run()

