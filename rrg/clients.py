import logging

from rrg.models import Client

logging.basicConfig(filename='testing.log', level=logging.DEBUG)
logger = logging.getLogger('test')

logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

"""
Basic Functions for Clients model
"""


def clients(session):
    """
    return list of all clients
    """
    return session.query(Client)


def clients_active(session):
    """
    return list of active clients
    """
    return session.query(Client).filter(Client.active==True)


def clients_inactive(session):
    """
    return list of inactive clients
    """
    return session.query(Client).filter(Client.active==False)


def picked_employee(session, number):
    clients = session.query(Client).all()
    return clients[number-1]


def selection_list(clients):
    tbl = []
    i = 1
    for e in clients:
        tbl.append([i, e.id, e.name, e.city, e.state.name,])
        i += 1
    return tbl


def selection_list_all(session):
    """
    return tabulated list of all clients
    :param session:
    
    :return:
    """
    return selection_list(clients(session))


def selection_list_active(session):
    """
    return tabulated list of active clients
    :param session:

    :return:
    """
    return selection_list(clients_active(session))



def selection_list_inactive(session):
    """
    return tabulated list of inactive clients
    :param session:

    :return:
    """
    return selection_list(clients_inactive(session))
