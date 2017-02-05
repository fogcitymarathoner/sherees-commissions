#!
import os
import argparse
import xml.etree.ElementTree as ET

from rrg.helpers import read_inv_xml_file
from rrg.models import invoice_archives
from rrg.utils import clients_ar_xml_file
from flask_script import Manager

from rrg import app

parser = argparse.ArgumentParser(description='RRG Accounts Receivable Reports')
parser.add_argument('type', help='report type',
                    choices=['all', 'open', 'pastdue', 'cleared'])
parser.add_argument(
    '--datadir', required=True,
    help='datadir dir with ar.xml',
    default='/php-apps/cake.rocketsredglare.com/rrg/data/')


def ar_report():
    """
    reads ar.xml, outputs tabbed report
    :param data_dir:
    :return:
    """
    args = parser.parse_args()

    print('Generating %s Report' % args.type)
    infile = clients_ar_xml_file(args.datadir)
    print('Parsing %s' % infile)
    if os.path.isfile(infile):
        tree = ET.parse(infile)
        root = tree.getroot()
        recs = invoice_archives(root, args.type)
        for i in recs:
            xmlpath = os.path.join(args.datadir, '%05d.xml' % int(i))
            date, amount, employee, voided = read_inv_xml_file(xmlpath)
            if not int(voided):
                print('%s %s %s %s' % (amount, date, voided, employee))
    else:
        print('No AR.xml file found')

manager = Manager(app)

@manager.command
def hello():
    print "hello"

if __name__ == "__main__":
    manager.run()