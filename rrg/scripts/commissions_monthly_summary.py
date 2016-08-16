
import argparse
from rrg.sherees_commissions import year_month_statement

monthy_statement_ym_header = '%s/%s - ###################################' \
                             '######################'

parser = argparse.ArgumentParser(description='RRG Sherees Monthly '
                                             'Commissions Reports')

parser.add_argument('year', type=int, help='commissions year')
parser.add_argument('month', type=int, help='commissions month')

parser.add_argument(
    '--datadir', required=True, help='datadir dir with ar.xml',
    default='/php-apps/cake.rocketsredglare.com/rrg/data/transactions/invoices/')


ledger_line_format = '%s %s %s %s'


def monthly_detail():
    args = parser.parse_args()

    print(monthy_statement_ym_header % (args.year, args.month))
    total, res = year_month_statement(args.datadir, args.year, args.month)
    print('Total %s ' % total)
    for i in res:
        print(ledger_line_format % (
            i['id'], i['date'], i['description'],
            i['amount']))
