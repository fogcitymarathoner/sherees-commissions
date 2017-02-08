import os
import argparse

from flask_script import Manager
from flask import Flask
from rrg.sherees_commissions import employee_year_month_statement
from rrg.models import session_maker
from rrg.models import Employee
from rrg.archive import employee as archived_employee
from rrg.utils import monthy_statement_ym_header

parser = argparse.ArgumentParser(description='RRG Sales Person Monthly Commissions Reports')

parser.add_argument('id', type=int, help='id from cached-employees report')
parser.add_argument('year', type=int, help='commissions year')
parser.add_argument('month', type=int, help='commissions month')

parser.add_argument('--db-user', required=True, help='database user', default='marcdba')
parser.add_argument('--mysql-host', required=True, help='database host - MYSQL_PORT_3306_TCP_ADDR', default='marcdba')
parser.add_argument('--mysql-port', required=True, help='database port - MYSQL_PORT_3306_TCP_PORT', default=3306)
parser.add_argument('--db', required=True, help='d', default='rrg')
parser.add_argument('--db-pass', required=True, help='database pw', default='deadbeef')
parser.add_argument('--datadir', required=True, help='datadir dir with ar.xml',
    default='/php-apps/cake.rocketsredglare.com/rrg/data/')

parser.add_argument('--cache', dest='cache', action='store_true')
parser.add_argument('--no-cache', dest='cache', action='store_false')
parser.set_defaults(cache=True)

ledger_line_format = '%s %s %s %s'

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


def monthly_detail():
    args = parser.parse_args()
    session = session_maker(args)
    print(monthy_statement_ym_header % (args.year, args.month))
    employee_dict = archived_employee(args.id, args.datadir)
    if employee_dict['salesforce']:
        employee = session.query(Employee).filter(Employee.id == employee_dict['id']).first()
        total, res = employee_year_month_statement(session, employee, args.datadir, args.year, args.month, args.cache)
        print('Total %s ' % total)
        for i in res:
            print(ledger_line_format % (
                i['id'], i['date'], i['description'],
                i['amount']))
    else:
        print('%s %s is not a sales person' % (employee_dict['firstname'], employee_dict['lastname']))
