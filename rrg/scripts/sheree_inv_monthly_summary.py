import os
import argparse
from flask_script import Manager
from flask import Flask
from rrg.sherees_commissions import invoice_report_month_year
from rrg.xml_helpers import monthy_statement_ym_header

parser = argparse.ArgumentParser(description='RRG Sherees Monthly Invoices Reports')
parser.add_argument('year', type=int, help='commissions year')
parser.add_argument('month', type=int, help='commissions month')

ledger_line_format = '%s %s %s %s'

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


def monthly_detail_ep():
    args = parser.parse_args()
    print(monthy_statement_ym_header % (args.year, args.month))
    total, res = invoice_report_month_year(args.datadir, args.month, args.year)
    print('Total %s ' % total)
    for i in res:
        print(ledger_line_format % (i['id'], i['date'], i['description'], i['amount']))


manager = Manager(app)


@manager.option('-m', '--month', help='month of report', required=True)
@manager.option('-y', '--year', help='year of report', required=True)
def monthly_detail(month, year):
    print(monthy_statement_ym_header % (year, month))
    total, res = invoice_report_month_year(app.config['DATADIR'], month, year)
    print('Total %s ' % total)
    for i in res:
        print(ledger_line_format % (i['id'], i['date'], i['description'], i['amount']))


if __name__ == "__main__":
    manager.run()


