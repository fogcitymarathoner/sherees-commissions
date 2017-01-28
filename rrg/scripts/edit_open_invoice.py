import os
from subprocess import call
import random
import string
import argparse
from datetime import datetime as dt
from datetime import timedelta as td
from tabulate import tabulate
import xml.etree.ElementTree as ET
import xml.dom.minidom as xml_pp

from rrg.reminders_generation import reminders as period_reminders
from rrg.reminders_generation import timecards_set
from rrg.invoices import open_invoices as sa_open_invoices
from rrg.invoices import picked_open_invoice
from rrg.models import Invoice
from rrg.models import Iitem
from rrg.models import session_maker

parser = argparse.ArgumentParser(description='RRG Edit Timecard')

parser.add_argument('number', type=int, help='reminder number to forget')
parser.add_argument('--db-user', required=True, help='database user',
                    default='marcdba')
parser.add_argument('--mysql-host', required=True,
                    help='database host - MYSQL_PORT_3306_TCP_ADDR',
                    default='marcdba')
parser.add_argument('--mysql-port', required=True,
                    help='database port - MYSQL_PORT_3306_TCP_PORT',
                    default=3306)
parser.add_argument('--db', required=True, help='d', default='rrg')
parser.add_argument('--db-pass', required=True, help='database pw',
                    default='deadbeef')


def edit_open_invoice():
    args = parser.parse_args()
    xml = None
    session = session_maker(args)

    w_open_invoices = sa_open_invoices(session)
    if args.number in xrange(1, w_open_invoices.count() + 1):
        open_invoice = picked_open_invoice(session, args)
        xml = xml_pp.parseString(ET.tostring(open_invoice.to_xml()))
        temp_file = os.path.join(os.path.sep, 'tmp', ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(40)))
        with open(temp_file, 'w+b') as f:
            f.write(xml.toprettyxml())
        call(["vi", temp_file])
        whole_inv_xml = Invoice.from_xml(temp_file)
        print 'inv from xml'
        print ET.tostring(whole_inv_xml)
        print 'inv from xml end'
        open_invoice.update_from_xml_doc(whole_inv_xml)
        print open_invoice.date
        print open_invoice.notes
        print whole_inv_xml
        print ET.tostring(whole_inv_xml)
        print whole_inv_xml.findall('invoice')
        print whole_inv_xml.findall('invoice/invoice-items')
        print whole_inv_xml.findall('invoice/invoice-items/invoice-item')
        for iitem in whole_inv_xml.iter('invoice-item'):
            print iitem.findall('id')[0].text
            iid = int(iitem.findall('id')[0].text)
            print 'updating item %s' % iid
            sa_item = session.query(Iitem).get(iid)
            sa_item.update_from_xml_doc(iitem)
            print sa_item.id
            print 'sa_item.quantity'
            print sa_item.quantity       
            print 'Open Invoice: %s' % args.number

        print 'Invoice Number: %s' % open_invoice.id
        print 'Date: %s' % open_invoice.date
        print 'Message: %s' % open_invoice.message
        print 'Notes: %s' % open_invoice.notes
        print 'Terms" %s' % open_invoice.terms
        print 'Client: %s' % open_invoice.contract.client.name
        print 'Employee: %s %s' % (open_invoice.contract.employee.firstname, open_invoice.contract.employee.lastname)
        print 'Period: %s-%s' % (open_invoice.period_start, open_invoice.period_end)
        i = 1
        for invoice_item in open_invoice.invoice_items:
            print 'Item: %s' % i
            print 'Description: %s' % invoice_item.description
            print 'Amount: %s' % invoice_item.amount
            print 'Quantity: %s' % invoice_item.quantity
        session.commit()
    else:
        print('Open Invoice number is not in range')
        quit()
