import argparse
from rrg.billing import cache_contract_items as routine
from rrg.models import session_maker

parser = argparse.ArgumentParser(description='RRG Cache Contract Items')

parser.add_argument(
    '--datadir', required=True,
    help='datadir dir',
    default='/php-apps/cake.rocketsredglare.com/rrg/data/contracts/contracts_items/')

parser.add_argument('--db-user', required=True, help='database user',
                    default='marcdba')
parser.add_argument('--mysql-host', required=True,
                    help='database host - MYSQL_PORT_3306_TCP_ADDR',
                    default='marcdba')
parser.add_argument('--mysql-port', required=True,
                    help='database port - MYSQL_PORT_3306_TCP_PORT',
                    default=3306)
parser.add_argument('--db', required=True, help='d', default='rrg')
parser.add_argument('--db-pass', required=True, help='database pw',
                    default='deadbeef')


def cache_contract_items():
    """
    cache contract items
    :param data_dir:
    :return:
    """
    args = parser.parse_args()
    session = session_maker(args)

    print('Caching Contract Items %s into %s' % (args.db, args.datadir))
    routine(session, args)
    session.commit()
