import logging
from rrg.models import Contract

logging.basicConfig(filename='testing.log', level=logging.DEBUG)
logger = logging.getLogger('test')

logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

"""
Basic Functions for Contract Model
"""


def contracts(session):
    """
    return list of all contracts
    """
    return session.query(Contract)


def contracts_items_active(session):
    """
    return list of active contracts
    """
    return session.query(Contract).filter(Contract.active==True)


def contracts_items_inactive(session):
    """
    return list of active contracts
    """
    return session.query(Contract).filter(Contract.active==False)


def selection_list(crypter, contracts):
    tbl = []
    for i, c in enumerate(contracts):

        tbl.append(
            [i + 1, c.id, c.client.name,
             '%s %s' % (c.employee.firstname, c.employee.lastname),
             c.startdate,
             c.enddate,
             ])
        i += 1
    return tbl


def selection_list_all(session, crypter):
    """
    return tabulated list of all contracts
    :param session:
    :param crypter:
    :return:
    """
    return selection_list(crypter, contracts(session))


def selection_list_active(session, crypter):
    """
    return tabulated list of active contracts
    :param session:
    :param crypter:
    :return:
    """
    return selection_list(crypter, contracts_items_active(session))


def deactivate_items_of_deactivated_contracts(session):
    """
    deactivate the items of inactive contracts
    """
    inactive_contracts = contracts_items_inactive(session)
    for contract in inactive_contracts:
        for item in contract.contract_items:
            if item.active is True:
                item.active = False
