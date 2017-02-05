#!
import os
import argparse
import xml.etree.ElementTree as ET

from flask_script import Manager
from flask import Flask
from rrg.helpers import read_inv_xml_file
from rrg.models import invoice_archives
from rrg.utils import clients_ar_xml_file

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
@manager.option('-t', '--type', help='type of ar report', choices=['all', 'open', 'pastdue', 'cleared'])
def report(type):

    print('Generating %s Report' % type)
    infile = clients_ar_xml_file(app.config['DATADIR'])
    print('Parsing %s' % infile)
    if os.path.isfile(infile):
        tree = ET.parse(infile)
        root = tree.getroot()
        recs = invoice_archives(root, type)
        for i in recs:
            xmlpath = os.path.join(app.config['DATADIR'], '%05d.xml' % int(i))
            date, amount, employee, voided = read_inv_xml_file(xmlpath)
            if not int(voided):
                print('%s %s %s %s' % (amount, date, voided, employee))
    else:
        print('No AR.xml file found')

if __name__ == "__main__":
    manager.run()