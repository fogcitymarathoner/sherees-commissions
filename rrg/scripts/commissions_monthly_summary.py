import argparse
from rrg.sherees_commissions import year_month_statement
from rrg.models import session_maker

monthy_statement_ym_header = '%s/%s - ###################################' \
                             '######################'

parser = argparse.ArgumentParser(description='RRG Sherees Monthly '
                                             'Commissions Reports')

parser.add_argument('year', type=int, help='commissions year')
parser.add_argument('month', type=int, help='commissions month')

parser.add_argument('--db-user', required=True, help='database user', default='marcdba')
parser.add_argument('--mysql-host', required=True, help='database host - MYSQL_PORT_3306_TCP_ADDR', default='marcdba')
parser.add_argument('--mysql-port', required=True, help='database port - MYSQL_PORT_3306_TCP_PORT', default=3306)
parser.add_argument('--db', required=True, help='d', default='rrg')
parser.add_argument('--db-pass', required=True, help='database pw', default='deadbeef')
parser.add_argument(
    '--datadir', required=True, help='datadir dir with ar.xml',
    default='/php-apps/cake.rocketsredglare.com/rrg/data/transactions/invoices/')


ledger_line_format = '%s %s %s %s'


def monthly_detail():
    args = parser.parse_args()

    session = session_maker(args)
    print(monthy_statement_ym_header % (args.year, args.month))
    total, res = year_month_statement(session, args)
    print('Total %s ' % total)
    for i in res:
        print(ledger_line_format % (
            i['id'], i['date'], i['description'],
            i['amount']))
