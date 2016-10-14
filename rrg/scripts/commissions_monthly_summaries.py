from rrg.models import session_maker

from datetime import datetime as dt
import argparse

from tabulate import tabulate

from rrg.sherees_commissions import employee_year_month_statement
from rrg.sherees_commissions import comm_months
from rrg.utils import monthy_statement_ym_header

parser = argparse.ArgumentParser(description='RRG Sherees Monthly Commissions Reports')

parser.add_argument(
    '--datadir', required=True,
    help='datadir dir with ar.xml',
    default='/php-apps/cake.rocketsredglare.com/rrg/data/transactions/'
            'invoices/invoice_items/commissions_items/')

parser.add_argument('--db-user', required=True, help='database user', default='marcdba')
parser.add_argument('--mysql-host', required=True, help='database host - MYSQL_PORT_3306_TCP_ADDR', default='marcdba')
parser.add_argument('--mysql-port', required=True, help='database port - MYSQL_PORT_3306_TCP_PORT', default=3306)
parser.add_argument('--db', required=True, help='d', default='rrg')
parser.add_argument('--db-pass', required=True, help='database pw', default='deadbeef')
parser.add_argument('--cache', dest='cache', action='store_true')
parser.add_argument('--no-cache', dest='cache', action='store_false')
parser.set_defaults(cache=True)


def monthlies_summary():
    args = parser.parse_args()

    session = session_maker(args)
    balance = 0
    for cm in comm_months(end=dt.now()):
        print(monthy_statement_ym_header % (cm['month'], cm['year']))
        args.year = cm['year']
        args.month = cm['month']
        total, res = employee_year_month_statement(session, args)
        balance += total
        res_dict_transposed = {
            'id': [''],
            'date': ['%s/%s' % (cm['month'], cm['year'])],
            'description': ['New Balance: %s' % balance],
            'amount': ['Period Total %s' % total]
        }
        print(tabulate(res_dict_transposed, headers='keys', tablefmt='plain'))
