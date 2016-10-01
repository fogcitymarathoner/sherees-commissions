import argparse
from rrg.billing import cache_non_date_parsed as routine
from rrg.models import InvoicePayment
from rrg.utils import transactions_invoice_payments_dir
from rrg.models import session_maker

parser = argparse.ArgumentParser(description='RRG Cache Invoice Payments')

parser.add_argument('project', help='project name', choices=['rrg', 'biz'])
parser.add_argument(
    '--datadir', required=True,
    help='datadir dir with invoice payments',
    default='/php-apps/cake.rocketsredglare.com/rrg/data/')

parser.add_argument('--db-user', required=True, help='database user', default='marcdba')
parser.add_argument('--mysql-host', required=True, help='database host - MYSQL_PORT_3306_TCP_ADDR', default='marcdba')
parser.add_argument('--mysql-port', required=True, help='database port - MYSQL_PORT_3306_TCP_PORT', default=3306)
parser.add_argument('--db', required=True, help='d', default='rrg')
parser.add_argument('--db-pass', required=True, help='database pw', default='deadbeef')


def cache_invoice_payments():
    """
    replaces cake cache commissions items
    """
    args = parser.parse_args()

    session = session_maker(args)

    print('Caching Invoice-Payments %s into %s' % (args.db, transactions_invoice_payments_dir(args.datadir)))
    routine(session, transactions_invoice_payments_dir(args.datadir), InvoicePayment)
    session.commit()
