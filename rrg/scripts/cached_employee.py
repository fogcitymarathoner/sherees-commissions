import os
import argparse

from flask_script import Manager
from flask import Flask
from rrg.archive import employee
from rrg.renderers import format_employee

parser = argparse.ArgumentParser(description='RRG Archived Employee')

parser.add_argument('id', type=int, help='id from cached-employees report')
parser.add_argument('--datadir', required=True, help='datadir dir with ar.xml',
    default='/php-apps/cake.rocketsredglare.com/rrg/data/')

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


def cached_employee():
    """
    prints selected archived employee
    :param data_dir:
    :return:
    """
    args = parser.parse_args()
    print('Archived Employee in %s' % args.datadir)
    employee_dict = employee(args.id, args.datadir)
    print format_employee(employee_dict)
