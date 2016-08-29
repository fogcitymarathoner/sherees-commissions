import argparse
from rrg.models import session_maker
from rrg.sherees_commissions import inv_report

monthy_statement_ym_header = '%s/%s - ###################################' \
                             '######################'

parser = argparse.ArgumentParser(description='RRG Sherees Monthly '
                                             'Invoices Reports')

parser.add_argument(
    '--datadir', required=True,
    help='datadir dir with ar.xml',
    default='/php-apps/cake.rocketsredglare.com/rrg/data/transactions/'
            'invoices/invoice_items/commissions_items/')

parser.add_argument(
    '--format', required=True, choices=['plain', 'latex'],
    help='output format', default='plain')

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
    print(inv_report(session, args))
