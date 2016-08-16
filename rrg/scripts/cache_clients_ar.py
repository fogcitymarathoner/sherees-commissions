import argparse
from rrg import cache_clients_ar

parser = argparse.ArgumentParser(description='RRG Cache Clients AR')

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


def cache_client_accounts_receivable():
    """
    replaces cake cache_client_ar
    :param data_dir:
    :return:
    """
    args = parser.parse_args()

    print('Caching Clients AR')
    cache_clients_ar(args)
