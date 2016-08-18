from rrg.reports.invoices import invoices_year_month

from rrg.models import session_maker

import argparse

from tabulate import tabulate

parser = argparse.ArgumentParser(description='RRG Invoices Year Month Report')

parser.add_argument('year', type=int, help='commissions year')
parser.add_argument('month', type=int, help='commissions month')

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


def invoices_monthly():
    args = parser.parse_args()

    session = session_maker(args)
    invs = invoices_year_month(session, args)

    res_dict_transposed = {
        'id': [i.id for i in invs],
        'date': [i.date for i in invs],
        'description': [
            '%s %s-%s' % (i.contract.title, i.period_start, i.period_end) for i
            in invs],
        'amount': [i.amount for i in invs]
    }
    print(tabulate(res_dict_transposed, headers='keys', tablefmt='plain'))