
import argparse
from rrg.sherees_commissions import cache_comm_items as \
    cache_commissions_items


parser = argparse.ArgumentParser(description='RRG Cache Commissions Items')


parser.add_argument('project', help='project name',
                    choices=['rrg', 'biz'])
parser.add_argument(
    '--datadir', required=True,
    help='datadir dir with ar.xml',
    default='/php-apps/cake.rocketsredglare.com/rrg/data/transactions/'
            'invoices/invoice_items/commissions_items/')


def cache_comm_items():
    """
    replaces cake cache commissions items
    """
    args = parser.parse_args()

    if args.project == 'rrg':
        print('Caching Commission Items')
        cache_commissions_items(args.datadir)
    else:
        print('Project not "rrg" skipping Caching Commission Items')