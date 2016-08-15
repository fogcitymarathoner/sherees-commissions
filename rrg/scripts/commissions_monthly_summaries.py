
from tabulate import tabulate
from datetime import datetime as dt


from rrg.sherees_commissions import year_month_statement
from rrg.sherees_commissions import comm_months

monthy_statement_ym_header = '%s/%s - ###################################' \
                             '######################'

from datetime import datetime as dt
import argparse

from tabulate import tabulate

from rrg.sherees_commissions import year_month_statement
from rrg.sherees_commissions import comm_months

monthy_statement_ym_header = '%s/%s - ###################################' \
                             '######################'

parser = argparse.ArgumentParser(description='RRG Sherees Monthly '
                                             'Commissions Reports')

parser.add_argument(
    '--datadir', required=True,
    help='datadir dir with ar.xml',
    default='/php-apps/cake.rocketsredglare.com/rrg/data/transactions/'
            'invoices/invoice_items/commissions_items/')


def monthlies_summary():

    args = parser.parse_args()

    balance = 0
    for cm in comm_months(end=dt.now()):
        print(monthy_statement_ym_header % (cm['month'], cm['year']))
        total, res = year_month_statement(args.datadir, cm['year'], cm['month'])
        balance += total

        res_dict_transposed = {
            'id': [''],
            'date': ['%s/%s' % (cm['month'], cm['year'])],
            'description': ['New Balance: %s' % balance],
            'amount': ['Period Total %s' % total]
        }
        print(tabulate(res_dict_transposed, headers='keys', tablefmt='plain'))
