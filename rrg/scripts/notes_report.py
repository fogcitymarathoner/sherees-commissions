import argparse
from rrg.sherees_commissions import sherees_notes_report
from rrg.models import session_maker

parser = argparse.ArgumentParser(description='RRG Sherees Notes Report')

parser.add_argument(
    '--format', required=True, choices=['plain', 'latex'],
    help='output format')


parser.add_argument('--db-user', required=True, help='database user', default='marcdba')
parser.add_argument('--mysql-host', required=True, help='database host - MYSQL_PORT_3306_TCP_ADDR', default='marcdba')
parser.add_argument('--mysql-port', required=True, help='database port - MYSQL_PORT_3306_TCP_PORT', default=3306)
parser.add_argument('--db', required=True, help='d', default='rrg')
parser.add_argument('--db-pass', required=True, help='database pw', default='deadbeef')


def notes():

    args = parser.parse_args()

    session = session_maker(args)
    if args.format == 'plain':
        print(sherees_notes_report(session, args))
    elif args.format == 'latex':
        print(sherees_notes_report(session, args))
