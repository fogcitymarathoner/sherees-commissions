
import os
from datetime import datetime as dt
from datetime import timedelta as td

from flask import Flask
from flask_script import Manager

from rrg.lib import reminders_generation
from rrg.models import session_maker

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



manager = Manager(app)


@manager.option(
    '-p', '--period', help='period type', choices=['week', 'biweek', 'semimonth', 'month'], required=True)
@manager.option('-n', '--number', help='index number', required=True)
def forget_numbered_reminder(period, number):
    session = session_maker(
        app.config['MYSQL_USER'], app.config['MYSQL_PASS'], app.config['MYSQL_SERVER_PORT_3306_TCP_ADDR'],
        app.config['MYSQL_SERVER_PORT_3306_TCP_PORT'], app.config['DB'])
    t_set = reminders_generation.timecards_set(session)
    w_reminders = reminders_generation.period_reminders(session, dt.now() - td(days=90), dt.now(), t_set, period)
    if int(number) in xrange(1, len(w_reminders) + 1):
        reminders_generation.forget_reminder(session, dt.now() - td(days=90), dt.now(), t_set, period, int(number))
        session.commit()
    else:
        print('Reminder number is not in range')
        quit()


if __name__ == "__main__":
    manager.run()
