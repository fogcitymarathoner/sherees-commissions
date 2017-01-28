import argparse
from datetime import datetime as dt
from datetime import timedelta as td
from tabulate import tabulate

from rrg.invoices import open_invoices as sa_open_invoices
from rrg.models import session_maker

parser = argparse.ArgumentParser(description='RRG Open Invoices')

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


def open_invoices():
    args = parser.parse_args()

    session = session_maker(args)

    w_open_invoices = sa_open_invoices(session)
    tbl = []
    i = 1
    for r in w_open_invoices:
        tbl.append(
            [i, r.contract.client.name, r.contract.employee.firstname + ' ' +
             r.contract.employee.lastname,
             dt.strftime(r.period_start, '%m/%d/%Y'), dt.strftime(r.period_end, '%m/%d/%Y')])
        i += 1
    print(
    tabulate(tbl, headers=['number', 'client', 'employee', 'start', 'end']))
