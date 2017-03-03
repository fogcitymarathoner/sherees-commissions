import argparse
import os

from flask import Flask
from flask_script import Manager

from rrg.lib import archive

parser = argparse.ArgumentParser(description='RRG Archived Contracts')

parser.add_argument(
    '--datadir', required=True, help='datadir root', default='/php-apps/cake.rocketsredglare.com/rrg/data/')

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


def cached_contracts_ep():
    """
    prints list of archived contracts for selection
    :param data_dir:
    :return:
    """
    args = parser.parse_args()
    print('Archived Contracts in %s' % args.datadir)
    archive.contracts(args.datadir)


manager = Manager(app)


def cached_contracts():

    print('Archived Contracts in %s' % app.config['DATADIR'])
    archive.contracts(app.config['DATADIR'])


if __name__ == "__main__":
    manager.run()


