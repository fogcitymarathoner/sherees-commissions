
from datetime import datetime as dt
import argparse
import xml.etree.ElementTree as ET
from rrg.models import Client
from rrg.models import Contract
from rrg.models import State
from rrg.models import User
from rrg.models import Invoice

from rrg.helpers import MissingEnvVar
from rrg.models import clients_ar_xml_file

parser = argparse.ArgumentParser(description='Rockets Redglare CLI.')
parser.add_argument('reminders', metavar='N', type=int, nargs='+', help='setup reminders for timecards')


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


def _is_pastdue(inv, date=None):
    """
    returns true or false if invoice is pastdue, server day
    :param inv:
    :param date:
    :return:
    """
    if not date:
        date = dt.now()
    if inv.duedate() < date:
        return True
    else:
        return False


def cache_clients_ar(session, datadir):
    #
    # Make sure destination directories exist
    #
    all_invs = session.query(Invoice)
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
                    if _is_pastdue(i, dt.now()):
                        id = ET.SubElement(pastdue, 'invoice')
                        id.text = str(i.id)
            else:
                id = ET.SubElement(cleared, 'invoice')
                id.text = str(i.id)
    tree = ET.ElementTree(doc)
    tree.write(clients_ar_xml_file(datadir))
    print('Wrote to %s' % clients_ar_xml_file(datadir))
