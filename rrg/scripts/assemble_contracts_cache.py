import argparse
import os

from flask import Flask
from flask_script import Manager

from rrg.lib import archive

parser = argparse.ArgumentParser(description='RRG Assemble Contracts Cache')
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


def assemble_contracts_cache_ep():
    """
    gathers contract items and invoices for contracts
    :param data_dir:
    :return:
    """
    args = parser.parse_args()
    print('Assembling Contracts in %s' % os.path.join(args.datadir, 'contracts'))
    archive.cached_contracts_collect_invoices_and_items(args.datadir)


manager = Manager(app)


@manager.command
def assemble_contracts_cache():
    print('Assembling Contracts in %s' % os.path.join(app.config['DATADIR'], 'contracts'))
    archive.cached_contracts_collect_invoices_and_items(app.config['DATADIR'])

if __name__ == "__main__":
    manager.run()

