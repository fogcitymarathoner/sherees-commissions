
import argparse
from rrg.sherees_commissions import cache_invoices as cache_invoices_routine
from rrg.models import session_maker

parser = argparse.ArgumentParser(description='RRG Cache Sherees Commissions Invoices')


parser.add_argument('project', help='project name',
                    choices=['rrg', 'biz'])
parser.add_argument(
    '--datadir', required=True,
    help='datadir dir with invoices',
    default='/php-apps/cake.rocketsredglare.com/rrg/data/transactions/invoices/invoice_items/commissions_items/'
            'invoices/')

parser.add_argument('--db-user', required=True, help='database user', default='marcdba')
parser.add_argument('--mysql-host', required=True, help='database host - MYSQL_PORT_3306_TCP_ADDR', default='marcdba')
parser.add_argument('--mysql-port', required=True, help='database port - MYSQL_PORT_3306_TCP_PORT', default=3306)
parser.add_argument('--db', required=True, help='d', default='rrg')
parser.add_argument('--db-pass', required=True, help='database pw', default='deadbeef')


def cache_invoices():
    """
    replaces cake cache commissions items
    """
    args = parser.parse_args()

    session = session_maker(args)

    print('Caching Sherees Invoices')
    cache_invoices_routine(session, args)
    session.commit()