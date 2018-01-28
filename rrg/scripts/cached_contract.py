import argparse
import os

from flask import Flask
from flask_script import Manager

from rrg.lib import archive

parser = argparse.ArgumentParser(description='RRG Archived Contract')

parser.add_argument('id', type=int, help='id from cached-contracts report')
parser.add_argument(
    '--datadir', required=True,
    help='datadir dir with ar.xml',
    default='/php-apps/cake.rocketsredglare.com/rrg/data/contracts/')

app = Flask(__name__, instance_relative_config=True)

# Load the default configuration
if os.environ.get('RRG_SETTINGS'):
    SETTINGS_FILE = os.environ.get('RRG_SETTINGS')
else:
    print('Environment Variable RRG_SETTINGS not set')
    quit(1)

if os.path.isfile(SETTINGS_FILE):
    try:
        app.config.from_envvar('RRG_SETTINGS')
    except Exception as e:
        print('something went wrong with config file %s' % SETTINGS_FILE)
        quit(1)
else:
    print('settings file %s does not exits' % SETTINGS_FILE)


def cached_contract_ep():
    """
    prints selected archived contract
    :param data_dir:
    :return:
    """
    args = parser.parse_args()

    print('Archived Contract in %s' % args.datadir)
    archive.contract(args.datadir, args.id)


manager = Manager(app)


@manager.option('-i', '--id', dest='id', required=True)
def cached_contract(id):

    print('Archived Contract in %s' % app.config['DATADIR'])
    archive.contract(app.config['DATADIR'], id)


if __name__ == "__main__":
    manager.run()


