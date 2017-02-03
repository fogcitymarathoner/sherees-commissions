import os
import argparse

from rrg.archive import cache_objs
from rrg.models import session_maker
from rrg.models import Vendor

parser = argparse.ArgumentParser(description='RRG Employees')

parser.add_argument(
    '--datadir', required=True,
    help='datadir dir',
    default='/php-apps/cake.rocketsredglare.com/rrg/data/')


parser.add_argument('--db-user', required=True, help='database user', default='marcdba')
parser.add_argument('--mysql-host', required=True, help='database host - MYSQL_PORT_3306_TCP_ADDR', default='marcdba')
parser.add_argument('--mysql-port', required=True, help='database port - MYSQL_PORT_3306_TCP_PORT', default=3306)
parser.add_argument('--db', required=True, help='d', default='rrg')
parser.add_argument('--db-pass', required=True, help='database pw', default='deadbeef')


def cache_vendors():
    """
    replaces cake cache_vendors
    :param data_dir:
    :return:
    """
    args = parser.parse_args()
    session = session_maker(args)

    print('Caching Vendors %s into %s' % (args.db, os.path.join(args.datadir, 'vendors')))
    vendors = session.query(Vendor).all()
    cache_objs(vendors)
    session.commit()
