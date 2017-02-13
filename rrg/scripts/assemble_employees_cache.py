import os
import argparse

from flask_script import Manager
from flask import Flask

from rrg.archive import cached_employees_collect_contracts as routine

parser = argparse.ArgumentParser(description='RRG Assemble Employees Cache')
parser.add_argument(
    '--datadir', required=True, help='data root directory', default='/php-apps/cake.rocketsredglare.com/rrg/data/')


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


def assemble_employees_cache_ep():
    """
    gathers contracts for employees
    :param data_dir:
    :return:
    """
    args = parser.parse_args()
    print('Assembling Employees in %s' % os.path.join(args.datadir, 'employees'))
    routine(args.datadir)


manager = Manager(app)


@manager.command
def assemble_employees_cache():
    print('Assembling Employees in %s' % os.path.join(app.config['DATADIR'], 'employees'))
    routine(app.config['DATADIR'])

if __name__ == "__main__":
    manager.run()
