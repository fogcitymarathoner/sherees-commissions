import argparse
from datetime import datetime as dt
from datetime import timedelta as td
from tabulate import tabulate
import xml.etree.ElementTree as ET
import xml.dom.minidom as xml_pp
from rrg.reminders_generation import reminders as period_reminders
from rrg.reminders_generation import timecards_set

from rrg.timecards import timecards as sa_timecards
from rrg.timecards import picked_timecard
from rrg.models import session_maker

parser = argparse.ArgumentParser(description='RRG Forget Reminder')

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


def view_timecard():
    args = parser.parse_args()
    xml = None
    session = session_maker(args)

    w_timecards = sa_timecards(session)
    if args.number in xrange(1, w_timecards.count() + 1):
        timecard = picked_timecard(session, args)
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
