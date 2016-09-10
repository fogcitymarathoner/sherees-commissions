import argparse
from rrg.billing import cache_clients as routine
from rrg.models import session_maker

parser = argparse.ArgumentParser(description='RRG Clients')

parser.add_argument(
    '--datadir', required=True,
    help='datadir dir',
    default='/php-apps/cake.rocketsredglare.com/rrg/data/clients/')

parser.add_argument('--db-user', required=True, help='database user',
                    default='marcdba')
parser.add_argument('--mysql-host', required=True,
                    help='database host - MYSQL_PORT_3306_TCP_ADDR',
                    default='marcdba')
parser.add_argument('--mysql-port', required=True,
                    help='database port - MYSQL_PORT_3306_TCP_PORT',
                    default=3306)
parser.add_argument('--db', required=True, help='database name', default='rrg')
parser.add_argument('--db-pass', required=True, help='database pw',
                    default='deadbeef')


def cache_clients():
    """
    replaces cake cache_clients
    :param data_dir:
    :return:
    """
    args = parser.parse_args()
    session = session_maker(args)

    print('Caching Clients %s' % args.db)
    routine(session, args)
    session.commit()
