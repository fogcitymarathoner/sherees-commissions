import argparse

from rrg.sherees_commissions import sherees_notes_report
from rrg.sherees_commissions import sherees_commissions_report
from rrg.sherees_commissions import comm_latex_document_header
from rrg.sherees_commissions import sheree_total_monies_owe
from rrg.models import session_maker

parser = argparse.ArgumentParser(description='RRG Sherees Commissions Report')

parser.add_argument(
    '--format', required=True, choices=['plain', 'latex'],
    help='output format', default='plain')

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

def monies_due():



    args = parser.parse_args()

    session = session_maker(args)

    print(sheree_total_monies_owe(session, args))