import argparse
from rrg.sherees_commissions import cache_comm_payments as cache_commissions_payments

from rrg.models import session_maker

parser = argparse.ArgumentParser(description='RRG Cache Commissions Payments')

parser.add_argument('project', help='project name', choices=['rrg', 'biz'])
parser.add_argument('--datadir', required=True, help='datadir dir with ar.xml',
    default='/php-apps/cake.rocketsredglare.com/rrg/data/')

parser.add_argument('--db-user', required=True, help='database user', default='marcdba')
parser.add_argument('--mysql-host', required=True, help='database host - MYSQL_PORT_3306_TCP_ADDR', default='marcdba')
parser.add_argument('--mysql-port', required=True, help='database port - MYSQL_PORT_3306_TCP_PORT', default=3306)
parser.add_argument('--db', required=True, help='d', default='rrg')
parser.add_argument('--db-pass', required=True, help='database pw', default='deadbeef')
parser.add_argument('--cache', dest='cache', action='store_true')
parser.add_argument('--no-cache', dest='cache', action='store_false')
parser.set_defaults(cache=True)


def cache_comm_payments():
    """
    replaces cake cache commissions payments
    """
    args = parser.parse_args()
    session = session_maker(args)
    if args.project == 'rrg':
        print('Caching Commission Payments')
        args.cache = False
        cache_commissions_payments(session, args.datadir, args.cache)
    else:
        print('Project not "rrg" skipping Caching Commission Items')
