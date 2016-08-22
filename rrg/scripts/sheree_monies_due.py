import argparse

from rrg.sherees_commissions import comm_latex_document_header
from rrg.sherees_commissions import sheree_total_monies_owed
from rrg.models import session_maker

parser = argparse.ArgumentParser(description='RRG Money Due to Sheree Summary Report')

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

    if args.format == 'plain':
        print(sheree_total_monies_owed(session, args))
    elif args.format == 'latex':
        report = comm_latex_document_header("Sheree's Monies Due Report")
        report += sheree_total_monies_owed(session, args)
        report += '\n\end{document}\n'
        print(report)
