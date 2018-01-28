import os
import argparse
import tabulate
from flask_script import Manager
from flask import Flask
from datetime import datetime as dt

from rrg.models_api import session_maker
from rrg.workers_comp import wc_report

def valid_date(s):
    try:
        return dt.strptime(s, "%Y-%m-%d")
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)

parser = argparse.ArgumentParser(description='RRG Workers Comp')

parser.add_argument('start_date', type=valid_date, help='first day of policy period - format YYYY-MM-DD ')
parser.add_argument('end_date', type=valid_date, help='last day of policy period - format YYYY-MM-DD ')
parser.add_argument('--db-user', required=True, help='database user', default='marcdba')
parser.add_argument('--mysql-host', required=True, help='database host - MYSQL_PORT_3306_TCP_ADDR', default='marcdba')
parser.add_argument('--mysql-port', required=True, help='database port - MYSQL_PORT_3306_TCP_PORT', default=3306)
parser.add_argument('--db', required=True, help='d', default='rrg')
parser.add_argument('--db-pass', required=True, help='database pw', default='deadbeef')

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


def workers_comp_report_ep():
    args = parser.parse_args()
    session = session_maker(args.db_user, args.db_pass, args.mysql_host, args.mysql_port, args.db)
    report = wc_report(session, args.start_date, args.end_date)
    print 'Workers comp report for %s - %s' % (args.start_date, args.end_date)
    for state in report:
        print 'State - %s' % state['state']
        data = []
        regular_total = 0
        overtime_total = 0
        doubletime_total = 0
        for d in state['employees']:
            data.append([d['employee'], d['regular'], d['overtime'], d['doubletime']])
            regular_total += d['regular']
            overtime_total += d['overtime']
            doubletime_total += d['doubletime']
        data.append(['', regular_total, overtime_total, doubletime_total])
        print tabulate.tabulate(data, headers=['employee', 'regular', 'overtime', 'doubletime'])


manager = Manager(app)


@manager.option('-s', '--start-date', dest='start_date', required=True)
@manager.option('-e', '--end-date', dest='end_date', required=True)
def workers_comp_report(start_date, end_date):
    session = session_maker(
        app.config['MYSQL_USER'], app.config['MYSQL_PASS'], app.config['MYSQL_SERVER_PORT_3306_TCP_ADDR'],
        app.config['MYSQL_SERVER_PORT_3306_TCP_PORT'], app.config['DB'])
    report = wc_report(session, start_date, end_date)
    print 'Workers comp report for %s - %s' % (start_date, end_date)
    for state in report:
        print 'State - %s' % state['state']
        data = []
        regular_total = 0
        overtime_total = 0
        doubletime_total = 0
        for d in state['employees']:
            data.append([d['employee'], d['regular'], d['overtime'], d['doubletime']])
            regular_total += d['regular']
            overtime_total += d['overtime']
            doubletime_total += d['doubletime']
        data.append(['', regular_total, overtime_total, doubletime_total])
        print tabulate.tabulate(data, headers=['employee', 'regular', 'overtime', 'doubletime'])
