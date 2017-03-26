import logging

import string

from rrg.models_api import employees, employees_active, employees_inactive
from rrg.models import employees_active
from rrg.models import employees_inactive

logging.basicConfig(filename='testing.log', level=logging.DEBUG)
logger = logging.getLogger('test')

logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


def selection_list(employees):
    printable = set(string.printable)
    tbl = []
    i = 1
    for e in employees:

        ssn = e.ssn_crypto
        bankaccountnumber = e.bankaccountnumber_crypto
        bankroutingnumber = e.bankroutingnumber_crypto
        tbl.append(
            [i, e.id, filter(lambda x: x in printable, e.firstname + ' ' +
             e.lastname),
             filter(lambda x: x in printable, ssn) if ssn else None,
             bankaccountnumber,
             bankroutingnumber,
            ])
        i += 1
    return tbl


def selection_list_all(session):
    """
    return tabulated list of all employees
    :param session:

    :return:
    """
    return selection_list(employees(session))


def selection_list_active(session):
    """
    return tabulated list of active employees
    :param session:

    :return:
    """
    return selection_list(employees_active(session))



def selection_list_inactive(session):
    """
    return tabulated list of inactive employees
    :param session:

    :return:
    """
    return selection_list(employees_inactive(session))
