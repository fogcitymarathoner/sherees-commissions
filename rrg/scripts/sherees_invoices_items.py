
import argparse
from rrg.sherees_commissions import invoices_items as sinvoices_items
from rrg.models import session_maker

parser = argparse.ArgumentParser(description='RRG Cache Sherees Commissions Invoices Items')


parser.add_argument('project', help='project name',
                    choices=['rrg', 'biz'])


parser.add_argument('--db-user', required=True, help='database user', default='marcdba')
parser.add_argument('--mysql-host', required=True, help='database host - MYSQL_PORT_3306_TCP_ADDR', default='marcdba')
parser.add_argument('--mysql-port', required=True, help='database port - MYSQL_PORT_3306_TCP_PORT', default=3306)
parser.add_argument('--db', required=True, help='d', default='rrg')
parser.add_argument('--db-pass', required=True, help='database pw', default='deadbeef')


def invoices_items():
    """
    replaces cake cache commissions items
    """
    args = parser.parse_args()

    session = session_maker(args)

    print('Sherees Invoices Items')
    sinvoices_items(session)
