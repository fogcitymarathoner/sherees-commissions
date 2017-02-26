import logging
from keyczar.errors import Base64DecodingError
import string
from rrg.models import Employee

logging.basicConfig(filename='testing.log', level=logging.DEBUG)
logger = logging.getLogger('test')

logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

"""
"""


def employees(session):
    """
    return list of all employees
    """
    return session.query(Employee)


def picked_employee(session, number):
    employees = session.query(Employee).all()
    return employees[number-1]


def selection_list(crypter, employees):
    printable = set(string.printable)
    tbl = []
    i = 1
    for e in employees:
        try:
            ssn = crypter.Decrypt(e.ssn_crypto)
        except Base64DecodingError:
            ssn = None
        try:
            bankaccountnumber = crypter.Decrypt(e.bankaccountnumber_crypto)
        except Base64DecodingError:
            bankaccountnumber = None
        try:
            bankroutingnumber = crypter.Decrypt(e.bankroutingnumber_crypto)
        except Base64DecodingError:
            bankroutingnumber = None
        tbl.append(
            [i, e.id, filter(lambda x: x in printable, e.firstname + ' ' +
             e.lastname),
             filter(lambda x: x in printable, ssn) if ssn else None,
             bankaccountnumber,
             bankroutingnumber,
            ])
        i += 1
    return tbl


def selection_list_all(session, crypter):
    """
    return tabulated list of all employees
    :param session:
    :param crypter:
    :return:
    """
    return selection_list(crypter, employees(session))