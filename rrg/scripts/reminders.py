from datetime import datetime as dt
from datetime import timedelta as td
from tabulate import tabulate

from rrg.reminders_generation import timecards_set
from rrg.reminders_generation import reminders


def week_reminders():
    t_set = timecards_set()
    wreminders = reminders(dt.now() - td(days=90), dt.now(), t_set, 'week')
    tbl = []
    for r in wreminders:
        tbl.append(
            [r[0].client.name, r[0].employee.firstname + ' ' +
             r[0].employee.lastname,
             dt.strftime(r[1], '%m/%d/%Y'), dt.strftime(r[2], '%m/%d/%Y')])
    print(tabulate(tbl, headers=['client', 'employee', 'start', 'end']))
