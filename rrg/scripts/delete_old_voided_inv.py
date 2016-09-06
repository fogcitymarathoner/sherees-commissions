import argparse

from rrg.maintenance import delete_old_void_invoices as routine
from rrg.models import session_maker

parser = argparse.ArgumentParser(description='RRG Delete Old Voided Invoices')

parser.add_argument('--db-user', required=True, help='database user', default='marcdba')
parser.add_argument('--mysql-host', required=True, help='database host - MYSQL_PORT_3306_TCP_ADDR', default='marcdba')
parser.add_argument('--mysql-port', required=True,  help='database port - MYSQL_PORT_3306_TCP_PORT', default=3306)
parser.add_argument('--db', required=True, help='d', default='rrg')
parser.add_argument('--db-pass', required=True, help='database pw', default='deadbeef')
parser.add_argument('--past-days', help='invoices older than reminders generator start date', default=91)


def delete_old_voided_invoices():
    """
    deletes voided invoices args.past_days old
    :return:
    """
    args = parser.parse_args()
    session = session_maker(args)
    routine(session, args)
    session.commit()
