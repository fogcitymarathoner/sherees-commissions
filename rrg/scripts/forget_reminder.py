import os
import argparse
from datetime import datetime as dt
from datetime import timedelta as td

from flask_script import Manager
from flask import Flask
from rrg.reminders_generation import reminders as period_reminders
from rrg.reminders_generation import timecards_set
from rrg.reminders_generation import forget_reminder
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

app = Flask(__name__, instance_relative_config=True)

# Load the default configuration
if os.environ.get('RRG_SETTINGS'):
    settings_file = os.environ.get('RRG_SETTINGS')
else:
    print('Environment Variable RRG_SETTINGS not set')
    quit(1)

if os.path.isfile(settings_file):
    try:
        app.config.from_envvar('RRG_SETTINGS')
    except Exception as e:
        print('something went wrong with config file %s' % settings_file)
        quit(1)
else:
    print('settings file %s does not exits' % settings_file)


def forget_numbered_reminder():
    args = parser.parse_args()

    session = session_maker(args)

    t_set = timecards_set(session, args)
    w_reminders = period_reminders(session, dt.now() - td(days=90), dt.now(),
                                   t_set, args)
    if args.number in xrange(1, len(w_reminders) + 1):
        forget_reminder(session, dt.now() - td(days=90), dt.now(), t_set, args)
        session.commit()
    else:
        print('Reminder number is not in range')
        quit()
