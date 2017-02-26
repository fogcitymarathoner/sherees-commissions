import logging
from keyczar.errors import Base64DecodingError
import string
from rrg.models import Employee

logging.basicConfig(filename='testing.log', level=logging.DEBUG)
logger = logging.getLogger('test')

logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

"""
Basic Functions for Employees model
"""


def employees(session):
    """
    return list of all employees
    """
    return session.query(Employee)


def employees_active(session):
    """
    return list of active employees
    """
    return session.query(Employee).filter(Employee.active==True)


def employees_inactive(session):
    """
    return list of inactive employees
    """
    return session.query(Employee).filter(Employee.active==False)


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



def selection_list_active(session, crypter):
    """
    return tabulated list of active employees
    :param session:
    :param crypter:
    :return:
    """
    return selection_list(crypter, employees_active(session))



def selection_list_inactive(session, crypter):
    """
    return tabulated list of inactive employees
    :param session:
    :param crypter:
    :return:
    """
    return selection_list(crypter, employees_inactive(session))
