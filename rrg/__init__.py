import os
import xml.etree.ElementTree as ET
from sqlalchemy.orm import sessionmaker

from rrg.models import Client
from rrg.models import Contract
from rrg.models import State
from rrg.models import User
from rrg.models import Invoice

from rrg.models import engine

from rrg.helpers import date_to_datetime


Session = sessionmaker(bind=engine)

session = Session()


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


def cache_clients_ar(data_dir):

    outfile = os.path.join(data_dir, 'ar.xml')
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
                    if i.is_pastdue():

                        id = ET.SubElement(pastdue, 'invoice')
                        id.text = str(i.id)
            else:
                id = ET.SubElement(cleared, 'invoice')
                id.text = str(i.id)

    tree = ET.ElementTree(doc)
    tree.write(outfile)

    print('Wrote to %s' % outfile)