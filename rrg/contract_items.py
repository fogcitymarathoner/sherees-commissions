import logging

from rrg.models import ContractItem

logging.basicConfig(filename='testing.log', level=logging.DEBUG)
logger = logging.getLogger('test')

logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

"""
Basic Functions for Citem Model
"""


def contracts_items(session):
    """
    return list of all contracts Items
    """
    return session.query(ContractItem)


def contracts_items_active(session):
    """
    return list of active contracts Items
    """
    return session.query(ContractItem).filter(ContractItem.active==True)


def contracts_items_active(session):
    """
    return list of active contracts Items
    """
    return session.query(ContractItem).filter(ContractItem.active==False)

