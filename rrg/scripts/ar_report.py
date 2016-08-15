import os
import argparse

import xml.etree.ElementTree as ET
from rrg.helpers import read_inv_xml_file
from rrg.models import invoice_archives

parser = argparse.ArgumentParser(description='RRG Accounts Receivable Reports')
parser.add_argument('type', help='report type',
                    choices=['all', 'open', 'pastdue', 'cleared'])
parser.add_argument(
    '--datadir', required=True,
    help='datadir dir with ar.xml',
    default='/php-apps/cake.rocketsredglare.com/rrg/data/'
            'transactions/invoices/"')


def ar_report():
    """
    reads ar.xml, outputs tabbed report
    :param data_dir:
    :return:
    """
    args = parser.parse_args()

    print('Generating %s Report' % type)
    infile = os.path.join(args.datadir, 'ar.xml')

    if os.path.isfile(infile):
        tree = ET.parse(infile)
        root = tree.getroot()
        if args.type == 'all':
            recs = invoice_archives(root, 'all')
        elif type == 'open':
            args.type = invoice_archives(root, 'open')
        elif type == 'pastdue':
            args.type = invoice_archives(root, 'pastdue')
        else:
            args.type = invoice_archives(root, 'cleared')

        # display invoices primatively
        for i in recs:
            xmlpath = os.path.join(datadir, '%05d.xml' % int(i))
            date, amount, employee, voided = read_inv_xml_file(xmlpath)
            if not int(voided):
                print('%s %s %s %s' % (amount, date, voided, employee))
    else:
        print('No AR.xml file found')
