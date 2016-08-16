from datetime import datetime as dt
from datetime import timedelta as td
from tabulate import tabulate

from rrg.reminders_generation import timecards_set
from rrg.reminders_generation import reminders as period_reminders
import argparse

parser = argparse.ArgumentParser(description='RRG Weekly Reminders')

parser.add_argument('--db-user', required=True, help='database user', default='marcdba')
parser.add_argument('--mysql-host', required=True, help='database host - MYSQL_PORT_3306_TCP_ADDR', default='marcdba')
parser.add_argument('--mysql-port', required=True, help='database port - MYSQL_PORT_3306_TCP_PORT', default=3306)
parser.add_argument('--db', required=True, help='d', default='rrg')
parser.add_argument('--db-pass', required=True, help='database pw', default='deadbeef')
parser.add_argument(
    '--period', required=True, help='period', default='week', choices=['week', 'biweek', 'semimonth', 'month'])


def reminders():

    args = parser.parse_args()

    t_set = timecards_set(args)
    w_reminders = period_reminders(dt.now() - td(days=90), dt.now(), t_set, args)
    tbl = []
    for r in w_reminders:
        tbl.append(
            [r[0].client.name, r[0].employee.firstname + ' ' +
             r[0].employee.lastname,
             dt.strftime(r[1], '%m/%d/%Y'), dt.strftime(r[2], '%m/%d/%Y')])
    print(tabulate(tbl, headers=['client', 'employee', 'start', 'end']))