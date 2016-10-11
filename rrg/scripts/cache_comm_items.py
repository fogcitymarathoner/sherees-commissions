import argparse
from rrg.sherees_commissions import cache_comm_items as cache_commissions_items
from rrg.models import session_maker
from rrg.utils import commissions_items_dir

parser = argparse.ArgumentParser(description='RRG Cache Commissions Items')

parser.add_argument('project', help='project name', choices=['rrg', 'biz'])
parser.add_argument(
    '--datadir', required=True,
    help='datadir dir with commissions items',
    default='/php-apps/cake.rocketsredglare.com/rrg/data/')

parser.add_argument('--db-user', required=True, help='database user', default='marcdba')
parser.add_argument('--mysql-host', required=True, help='database host - MYSQL_PORT_3306_TCP_ADDR', default='marcdba')
parser.add_argument('--mysql-port', required=True, help='database port - MYSQL_PORT_3306_TCP_PORT', default=3306)
parser.add_argument('--db', required=True, help='d', default='rrg')
parser.add_argument('--db-pass', required=True, help='database pw', default='deadbeef')


def cache_comm_items():
    """
    replaces cake cache commissions items
    """
    args = parser.parse_args()

    session = session_maker(args)
    if args.project == 'rrg':
        print('Caching Commission Items into %s' % commissions_items_dir(args.datadir))
        cache_commissions_items(session, args.datadir)
    else:
        print('Project not "rrg" skipping Caching Commission Items')
