import os
import argparse
from flask_script import Manager
from flask import Flask
import xml.etree.ElementTree as ET
import xml.dom.minidom as xml_pp

from rrg.models import open_timecards
from rrg.models import picked_timecard
from rrg.models import session_maker

parser = argparse.ArgumentParser(description='RRG Forget Reminder')

parser.add_argument('number', type=int, help='reminder number to forget')
parser.add_argument('--db-user', required=True, help='database user', default='marcdba')
parser.add_argument('--mysql-host', required=True, help='database host - MYSQL_PORT_3306_TCP_ADDR', default='marcdba')
parser.add_argument('--mysql-port', required=True, help='database port - MYSQL_PORT_3306_TCP_PORT', default=3306)
parser.add_argument('--db', required=True, help='d', default='rrg')
parser.add_argument('--db-pass', required=True, help='database pw', default='deadbeef')

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


def view_timecard_ep():
    args = parser.parse_args()
    session = session_maker(args.db_user, args.db_pass, args.mysql_host, args.mysql_port, args.db)
    w_timecards = open_timecards(session)
    if args.number in xrange(1, w_timecards.count() + 1):
        timecard = picked_timecard(session, args.number)
        xml = xml_pp.parseString(ET.tostring(timecard.to_xml()))
        print xml.toprettyxml()
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
    else:
        print('Timecard number is not in range')
        quit()


manager = Manager(app)


@manager.option('-n', '--number', dest='number', default=True)
def view_timecard(number):
    session = session_maker(
        app.config['MYSQL_USER'], app.config['MYSQL_PASS'], app.config['MYSQL_SERVER_PORT_3306_TCP_ADDR'],
        app.config['MYSQL_SERVER_PORT_3306_TCP_PORT'], app.config['DB'])
    w_timecards = open_timecards(session)
    if number in xrange(1, w_timecards.count() + 1):
        timecard = picked_timecard(session, number)
        xml = xml_pp.parseString(ET.tostring(timecard.to_xml()))
        print xml.toprettyxml()
        print 'Timecard: %s' % number
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
    else:
        print('Timecard number is not in range')
        quit()

