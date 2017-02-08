import os
from datetime import datetime as dt
import argparse

from flask_script import Manager
from flask import Flask
from tabulate import tabulate

from rrg.models import session_maker
from rrg.models import Employee
from rrg.sherees_commissions import employee_year_month_statement
from rrg.sherees_commissions import comm_months
from rrg.utils import monthy_statement_ym_header

parser = argparse.ArgumentParser(description='RRG All Sales People Monthly Commissions Reports')

parser.add_argument(
    '--datadir', required=True,
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


def monthlies_summary():
    args = parser.parse_args()
    session = session_maker(args)
    salespeople = session.query(Employee).filter(Employee.salesforce==True)
    for salesperson in salespeople:
        balance = 0
        for cm in comm_months(end=dt.now()):
            print('%s %s' % (salesperson.firstname, salesperson.lastname))
            print(monthy_statement_ym_header % (cm['month'], cm['year']))
            year = cm['year']
            month = cm['month']
            # employee_year_month_statement(session, employee, datadir, year, month, cache)
            total, res = employee_year_month_statement(session, salesperson, args.datadir, year, month, args.cache)
            balance += total
            res_dict_transposed = {
                'id': [''],
                'date': ['%s/%s' % (cm['month'], cm['year'])],
                'description': ['New Balance: %s' % balance],
                'amount': ['Period Total %s' % total]
            }
            print(tabulate(res_dict_transposed, headers='keys', tablefmt='plain'))
