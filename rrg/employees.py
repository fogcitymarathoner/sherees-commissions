from datetime import datetime as dt
import hashlib
import logging
from sqlalchemy import and_
from s3_mysql_backup import YMD_FORMAT

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

def picked_employee(session, args):
    employees = session.query(Employee).all()
    return employees[args.number-1]

