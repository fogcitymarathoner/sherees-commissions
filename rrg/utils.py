
from tabulate import tabulate
from datetime import datetime as dt

from rrg import engine
from rrg.models import Contract
from rrg.models import Base

from rrg.sherees_commissions import year_month_statement
from rrg.sherees_commissions import comm_months


def clear_out_bad_contracts():
    """
    removed contracts from the database that have either employee_id or
    client_id 0 or None
    """
    session.query(
        Contract).filter(
        Contract.employee_id == 0, Contract.client_id == 0).delete(
        synchronize_session=False)
    session.commit()


def create_db():
    """
    this routine has a bug, DATABASE isn't fully integrated right, the line
    DATABASE = 'rrg' in rrg/__init__.py has to be temporarily hardcoded to
    'rrg_test' or whatever
    :return:
    """
    Base.metadata.create_all(engine)


monthy_statement_ym_header = '%s/%s - ###################################' \
                             '######################'


def test_summary(data_dir='/php-apps/cake.rocketsredglare.com/rrg/data/'
                          'transactions/invoices/invoice_items/'
                          'commissions_items/'):
    balance = 0
    for cm in comm_months(end=dt.now()):
        print(monthy_statement_ym_header % (cm['month'], cm['year']))
        sum, res = year_month_statement(data_dir, cm['year'], cm['month'])
        balance += sum

        res_dict_transposed = {
            'id': [''],
            'date': ['%s/%s' % (cm['month'], cm['year'])],
            'description': ['New Balance: %s' % balance],
            'amount': ['Period Total %s' % sum]
        }
        print(tabulate(res_dict_transposed, headers='keys', tablefmt='plain'))
