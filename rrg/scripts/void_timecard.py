import os
import argparse
from flask_script import Manager
from flask import Flask

from rrg.timecards import void_timecard as process
from rrg.timecards import timecards as sa_timecards
from rrg.models import session_maker

parser = argparse.ArgumentParser(description='RRG Forget Reminder')

parser.add_argument('number', type=int, help='reminder number to forget')
parser.add_argument('--db-user', required=True, help='database user', default='marcdba')
parser.add_argument('--mysql-host', required=True, help='database host - MYSQL_PORT_3306_TCP_ADDR', default='marcdba')
parser.add_argument('--mysql-port', required=True, help='database port - MYSQL_PORT_3306_TCP_PORT', default=3306)
parser.add_argument('--db', required=True, help='d', default='rrg')
parser.add_argument('--db-pass', required=True, help='database pw', default='deadbeef')

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


def void_timecard_ep():
    args = parser.parse_args()
    session = session_maker(args.db_user, args.db_pass, args.mysql_host, args.mysql_port, args.db)
    w_timecards = sa_timecards(session)
    if args.number in xrange(1, w_timecards.count() + 1):
        process(session, args.number)
        session.commit()
    else:
        print('Timecard number is not in range')
        quit()


manager = Manager(app)


@manager.option('-n', '--number', dest='number', default=True)
def void_timecard(number):
    session = session_maker(
        app.config['MYSQL_USER'], app.config['MYSQL_PASS'], app.config['MYSQL_SERVER_PORT_3306_TCP_ADDR'],
        app.config['MYSQL_SERVER_PORT_3306_TCP_PORT'], app.config['DB'])
    w_timecards = sa_timecards(session)
    if number in xrange(1, w_timecards.count() + 1):
        process(session, number)
        session.commit()
    else:
        print('Timecard number is not in range')
        quit()

