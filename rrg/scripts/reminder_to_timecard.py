import argparse
from datetime import datetime as dt
from datetime import timedelta as td

from rrg.reminders_generation import reminders as period_reminders
from rrg.reminders_generation import timecards_set
from rrg.reminders_generation import reminder_to_timecard as process
from rrg.models import session_maker

parser = argparse.ArgumentParser(description='RRG Forget Reminder')

parser.add_argument('number', type=int, help='reminder number to forget')
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
parser.add_argument(
    '--period', required=True, help='period', default='week',
    choices=['week', 'biweek', 'semimonth', 'month'])


def reminder_to_timecard():
    args = parser.parse_args()

    session = session_maker(args)

    t_set = timecards_set(session, args)
    w_reminders = period_reminders(session, dt.now() - td(days=90), dt.now(),
                                   t_set, args)
    if args.number in xrange(1, len(w_reminders) + 1):
        process(session, dt.now() - td(days=90), dt.now(), t_set, args)
        session.commit()
    else:
        print('Reminder number is not in range')
        quit()
