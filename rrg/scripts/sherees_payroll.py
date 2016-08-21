import argparse

from rrg.sherees_commissions import payroll_due_report
from rrg.models import session_maker
from rrg.sherees_commissions import comm_latex_document_header

parser = argparse.ArgumentParser(description='RRG Sherees Commissions Report')

parser.add_argument(
    '--format', required=True, choices=['plain', 'latex'],
    help='output format', default='plain')
parser.add_argument('--db-user', required=True, help='database user', default='marcdba')
parser.add_argument('--mysql-host', required=True, help='database host - MYSQL_PORT_3306_TCP_ADDR', default='marcdba')
parser.add_argument('--mysql-port', required=True, help='database port - MYSQL_PORT_3306_TCP_PORT', default=3306)
parser.add_argument('--db', required=True, help='d', default='rrg')
parser.add_argument('--db-pass', required=True, help='database pw', default='deadbeef')


def sherees_payroll():
    args = parser.parse_args()

    session = session_maker(args)

    if args.format == 'latex':
        report = comm_latex_document_header("Sheree's Hourly")
        report += payroll_due_report(session, args)(session, args)
        report += '\n\end{document}\n'
        print(report)
    else:
        print(payroll_due_report(session, args)(session, args))
