import os
from flask_script import Manager
from flask import Flask

from rrg.models import void_timecard as process
from rrg.models_api import open_timecards, void_timecard, session_maker
from rrg.models import session_maker


app = Flask(__name__, instance_relative_config=True)

# Load the default configuration
if os.environ.get('RRG_SETTINGS'):
    SETTINGS_FILE = os.environ.get('RRG_SETTINGS')
else:
    print('Environment Variable RRG_SETTINGS not set')
    quit(1)

if os.path.isfile(SETTINGS_FILE):
    try:
        app.config.from_envvar('RRG_SETTINGS')
    except Exception as e:
        print('something went wrong with config file %s' % SETTINGS_FILE)
        quit(1)
else:
    print('settings file %s does not exits' % SETTINGS_FILE)


manager = Manager(app)


@manager.option('-n', '--number', dest='number', default=True)
def void_timecard(number):
    print("Voiding Timecard Number %s" % number)
    session = session_maker(
        app.config['MYSQL_USER'], app.config['MYSQL_PASS'], app.config['MYSQL_SERVER_PORT_3306_TCP_ADDR'],
        app.config['MYSQL_SERVER_PORT_3306_TCP_PORT'], app.config['DB'])
    w_timecards = open_timecards(session)
    if int(number) in [i for i in xrange(1, w_timecards.count() + 1)]:
        process(session, int(number))
        session.commit()
    else:
        print('Timecard number is not in range')
        quit()


if __name__ == "__main__":
    manager.run()
