import argparse
from rrg import cache_clients_ar

parser = argparse.ArgumentParser(description='RRG Cache Clients AR')

parser.add_argument(
    '--datadir', required=True,
    help='datadir dir with ar.xml',
    default='/php-apps/cake.rocketsredglare.com/rrg/data/transactions/'
            'invoices/invoice_items/commissions_items/"')


def cache_client_accounts_receivable():
    """
    replaces cake cache_client_ar
    :param data_dir:
    :return:
    """
    args = parser.parse_args()

    print('Caching Clients AR')
    cache_clients_ar(args.datadir)
