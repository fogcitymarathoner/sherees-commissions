
import argparse

from rrg.sherees_commissions import sherees_commissions_report

parser = argparse.ArgumentParser(description='RRG Sherees Commissions Report')

parser.add_argument(
    '--format', required=True, choices=['plain', 'latex'],
    help='output format', default='plain')

parser.add_argument(
    '--datadir', required=True,
    help='datadir dir with ar.xml',
    default='/php-apps/cake.rocketsredglare.com/rrg/data/transactions/'
            'invoices/invoice_items/commissions_items/')


def comm():

    args = parser.parse_args()

    print(sherees_commissions_report(
        data_dir=args.datadir, format=args.format))
