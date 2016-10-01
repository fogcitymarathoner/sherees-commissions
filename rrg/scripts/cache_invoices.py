import argparse
from rrg.billing import cache_non_date_parsed as cache_routine
from rrg.models import session_maker
from rrg.utils import transactions_invoices_dir

parser = argparse.ArgumentParser(description='RRG Cache Invoices')

parser.add_argument('project', help='project name',
                    choices=['rrg', 'biz'])
parser.add_argument(
    '--datadir', required=True, help='datadir dir with invoices',
    default='/php-apps/cake.rocketsredglare.com/rrg/data/')

parser.add_argument('--mysql-host', required=True, help='database host - MYSQL_PORT_3306_TCP_ADDR', default='marcdba')
parser.add_argument('--mysql-port', required=True, help='database port - MYSQL_PORT_3306_TCP_PORT', default=3306)
parser.add_argument('--db', required=True, help='d', default='rrg')
parser.add_argument('--db-user', required=True, help='database user', default='marcdba')
parser.add_argument('--db-pass', required=True, help='database pw', default='deadbeef')


def cache_invoices():
    """
    replaces cake cache commissions items
    """
    args = parser.parse_args()
    session = session_maker(args)
    print('Caching Invoices %s into %s' % (args.db, transactions_invoices_dir(args.datadir)))
    cache_routine(session, args.datadir)
    session.commit()
