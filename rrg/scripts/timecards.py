import os
import argparse
from flask_script import Manager
from flask import Flask
from datetime import datetime as dt
from tabulate import tabulate

from rrg.timecards import timecards as sa_timecards
from rrg.models import session_maker

parser = argparse.ArgumentParser(description='RRG Pending Invoices')

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


def timecards():
    args = parser.parse_args()

    session = session_maker(args)

    w_timecards = sa_timecards(session)
    tbl = []
    i = 1
    for r in w_timecards:
        tbl.append(
            [i, r.contract.client.name, r.contract.employee.firstname + ' ' +
             r.contract.employee.lastname,
             dt.strftime(r.period_start, '%m/%d/%Y'), dt.strftime(r.period_end, '%m/%d/%Y')])
        i += 1
    print(
    tabulate(tbl, headers=['number', 'client', 'employee', 'start', 'end']))
