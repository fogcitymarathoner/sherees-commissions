import argparse
import tabulate
from datetime import datetime as dt
from datetime import timedelta as td

from rrg.models import session_maker
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

def workers_comp_report():
    args = parser.parse_args()

    session = session_maker(args)
    report =  wc_report(session, args)
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
