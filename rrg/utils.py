import os
from tabulate import tabulate
from datetime import datetime as dt
from datetime import timedelta as td
import xml.etree.ElementTree as ET
import argparse

from rrg.helpers import read_inv_xml_file
from rrg.models import invoice_archives
from rrg import session
from rrg.models import Contract
from rrg.models import Base
from rrg import engine
from rrg.reminders_generation import timecards_set
from rrg.reminders_generation import reminders


def clear_out_bad_contracts():
    """
    removed contracts from the database that have either employee_id or client_id 0 or None
    """
    session.query(Contract).filter(Contract.employee_id == 0, Contract.client_id ==0).delete(synchronize_session=False)
    session.commit()


def create_db():
    """
    this routine has a bug, DATABASE isn't fully integrated right, the line

        DATABASE = 'rrg' in rrg/__init__.py has to be temporarily hardcoded to 'rrg_test' or whatever
    :return:
    """
    Base.metadata.create_all(engine)


def week_reminders():
    t_set = timecards_set()
    wreminders = reminders(dt.now() - td(days=90), dt.now(), t_set, 'week')
    tbl = []
    for r in wreminders:
        tbl.append([r[0].client.name, r[0].employee.firstname+' '+r[0].employee.lastname,
            dt.strftime(r[1], '%m/%d/%Y'), dt.strftime(r[2], '%m/%d/%Y')])
    print(tabulate(tbl, headers=['client', 'employee', 'start', 'end']))


parser = argparse.ArgumentParser(description='RRG Accounts Receivable Reports')
parser.add_argument('type', help='report type' , choices=['all', 'open', 'pastdue', 'cleared'])
parser.add_argument(
    '--datadir', required = True,
    help='datadir dir with ar.xml "/php-apps/cake.rocketsredglare.com/rrg/data/'
    'transactions/invoices/"')

def ar_report():
    """
    reads ar.xml, outputs tabbed report
    :param data_dir:
    :return:
    """
    args = parser.parse_args()
    datadir = args.datadir
    type = args.type
    print('Generating %s Report' % type)
    infile = os.path.join(datadir, 'ar.xml')

    if os.path.isfile(infile):
        tree = ET.parse(infile)
        root = tree.getroot()
        if type == 'all':
            recs = invoice_archives(root, 'all')
        elif type == 'open':
            recs = invoice_archives(root, 'open')
        elif type == 'pastdue':
            recs = invoice_archives(root, 'pastdue')
        else:
            recs = invoice_archives(root, 'cleared')

        # display invoices primatively
        for i in recs:
            xmlpath = os.path.join(datadir, '%05d.xml' % int(i))
            date, amount, employee, voided = read_inv_xml_file(xmlpath)
            if not int(voided):
                print('%s %s %s %s' % (amount,  date,  voided, employee))
    else:
        print('No AR.xml file found')
