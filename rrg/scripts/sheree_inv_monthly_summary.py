import argparse
from rrg.sherees_commissions import invoice_report_month_year

monthy_statement_ym_header = '%s/%s - ###################################' \
                             '######################'
parser = argparse.ArgumentParser(description='RRG Sherees Monthly '
                                             'Invoices Reports')
parser.add_argument('year', type=int, help='commissions year')
parser.add_argument('month', type=int, help='commissions month')

ledger_line_format = '%s %s %s %s'


def monthly_detail():
    args = parser.parse_args()
    print(monthy_statement_ym_header % (args.year, args.month))
    total, res = invoice_report_month_year(args)
    print('Total %s ' % total)
    for i in res:
        print(ledger_line_format % (
            i['id'], i['date'], i['description'],
            i['amount']))
