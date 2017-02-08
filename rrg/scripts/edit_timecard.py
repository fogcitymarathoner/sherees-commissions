import os
from subprocess import call
import random
import string
import argparse

from flask_script import Manager
from flask import Flask
import xml.etree.ElementTree as ET
import xml.dom.minidom as xml_pp

from rrg.timecards import timecards as sa_timecards
from rrg.timecards import picked_timecard
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

app = Flask(__name__, instance_relative_config=True)

# Load the default configuration
if os.environ.get('RRG_SETTINGS'):
    settings_file = os.environ.get('RRG_SETTINGS')
else:
    print('Environment Variable RRG_SETTINGS not set')
    quit(1)

if os.path.isfile(settings_file):
    try:
        app.config.from_envvar('RRG_SETTINGS')
    except Exception as e:
        print('something went wrong with config file %s' % settings_file)
        quit(1)
else:
    print('settings file %s does not exits' % settings_file)


def edit_timecard():
    args = parser.parse_args()
    xml = None
    session = session_maker(args)

    w_timecards = sa_timecards(session)
    if args.number in xrange(1, w_timecards.count() + 1):
        timecard = picked_timecard(session, args)
        xml = xml_pp.parseString(ET.tostring(timecard.to_xml()))
        temp_file = os.path.join(os.path.sep, 'tmp', ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(40)))
        with open(temp_file, 'w+b') as f:
            f.write(xml.toprettyxml())
        call(["vi", temp_file])
        whole_inv_xml = Invoice.from_xml(temp_file)
        print 'inv from xml'
        print ET.tostring(whole_inv_xml)
        print 'inv from xml end'
        timecard.update_from_xml_doc(whole_inv_xml)
        print timecard.date
        print timecard.notes
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
            print 'Timecard: %s' % args.number

        print 'Invoice Number: %s' % timecard.id
        print 'Date: %s' % timecard.date
        print 'Message: %s' % timecard.message
        print 'Notes: %s' % timecard.notes
        print 'Terms" %s' % timecard.terms
        print 'Client: %s' % timecard.contract.client.name
        print 'Employee: %s %s' % (timecard.contract.employee.firstname, timecard.contract.employee.lastname)
        print 'Period: %s-%s' % (timecard.period_start, timecard.period_end)
        i = 1
        for invoice_item in timecard.invoice_items:
            print 'Item: %s' % i
            print 'Description: %s' % invoice_item.description
            print 'Amount: %s' % invoice_item.amount
            print 'Quantity: %s' % invoice_item.quantity
        session.commit()
    else:
        print('Timecard number is not in range')
        quit()
