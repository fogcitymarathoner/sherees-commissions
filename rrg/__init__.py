import os
from datetime import datetime as dt
import argparse
import xml.etree.ElementTree as ET
from rrg.models import Client
from rrg.models import Contract
from rrg.models import State
from rrg.models import User
from rrg.models import Invoice
from rrg.models import is_pastdue
from rrg.models import session_maker
from rrg.helpers import date_to_datetime
from rrg.helpers import MissingEnvVar


try:
    env_str = 'DB_USER'
    if os.getenv(env_str) is None:
        raise MissingEnvVar('%s is not set' % env_str)
    else:
        DB_USER = os.getenv(env_str)

    env_str = 'DB_PASS'
    if os.getenv(env_str) is None:
        raise MissingEnvVar('%s is not set' % env_str)
    else:
        DB_PASS = os.getenv(env_str)

    env_str = 'MYSQL_SERVER_PORT_3306_TCP_ADDR'
    if os.getenv(env_str) is None:
        raise MissingEnvVar('%s is not set' % env_str)
    else:
        MYSQL_PORT_3306_TCP_ADDR = os.getenv(env_str)

    env_str = 'MYSQL_SERVER_PORT_3306_TCP_PORT'
    if os.getenv(env_str) is None:
        raise MissingEnvVar('%s is not set' % env_str)
    else:
        MYSQL_PORT_3306_TCP_PORT = os.getenv(env_str)
    DATABASE = 'rrg'

    env_str = 'DATABASE'
    if os.getenv(env_str) is None:
        raise MissingEnvVar('%s is not set' % env_str)
    else:
        DATABASE = os.getenv(env_str)

except MissingEnvVar as e:
    print(e.value)
    raise


parser = argparse.ArgumentParser(description='Rockets Redglare CLI.')
parser.add_argument('reminders', metavar='N', type=int, nargs='+',
                    help='setup reminders for timecards')


def cleared_invoices_client(client, all_invs):
    """
    filters out clients cleared invoices
    :param client:
    :param all_invs:
    :return:
    """
    cleared_invoices = []
    for i in all_invs:
        if i.contract.client == client and i.posted and not i.voided and i.cleared:

            cleared_invoices.append(i)
    return cleared_invoices


def open_invoices_client(client, all_invs):
    """
    filters out clients open invoices
    :param client:
    :param all_invs:
    :return:
    """
    open_invoices = []
    for i in all_invs:
        if i.contract.client == client and i.posted and i.voided is False and i.cleared is False:
            open_invoices.append(i)
        print(i)
    return open_invoices


def cache_clients_ar(args):

    session = session_maker(args)
    outfile = os.path.join(args.datadir, 'ar.xml')
    all_invs = session.query(Invoice).order_by(Invoice.date)

    doc = ET.Element('invoices')
    all = ET.SubElement(doc, 'all')
    open = ET.SubElement(doc, 'open')
    pastdue = ET.SubElement(doc, 'pastdue')
    cleared = ET.SubElement(doc, 'cleared')

    for i in all_invs:
        if not i.voided:
            id = ET.SubElement(all, 'invoice')
            id.text = str(i.id)
            if not i.cleared:

                id = ET.SubElement(open, 'invoice')
                id.text = str(i.id)
                if i.date:
                    if is_pastdue(i, dt.now()):
                        id = ET.SubElement(pastdue, 'invoice')
                        id.text = str(i.id)
            else:
                id = ET.SubElement(cleared, 'invoice')
                id.text = str(i.id)

    tree = ET.ElementTree(doc)
    tree.write(outfile)

    print('Wrote to %s' % outfile)


def main():

    args = parser.parse_args()
    print(args)
    print('hi world!')

