import argparse
import os

from flask import Flask
from flask_script import Manager

from rrg import utils
from rrg.models import Vendor
from rrg.models import session_maker

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


def cache_vendors_ep():
    """
    replaces cake cache_vendors
    :param data_dir:
    :return:
    """
    args = parser.parse_args()
    session = session_maker(args.db_user, args.db_pass, args.mysql_host, args.mysql_port, args.db)

    print('Caching Vendors %s into %s' % (args.db, os.path.join(args.datadir, 'vendors')))
    vendors = session.query(Vendor).all()
    utils.cache_objs(args.datadir, vendors)
    session.commit()


manager = Manager(app)


def cache_vendors():
    session = session_maker(
        app.config['MYSQL_USER'], app.config['MYSQL_PASS'], app.config['MYSQL_SERVER_PORT_3306_TCP_ADDR'],
        app.config['MYSQL_SERVER_PORT_3306_TCP_PORT'], app.config['DB'])

    print('Caching Vendors %s into %s' % (app.config['DB'], os.path.join(app.config['DATADIR'], 'vendors')))
    vendors = session.query(Vendor).all()
    utils.cache_objs(app.config['DATADIR'], vendors)
    session.commit()


if __name__ == "__main__":
    manager.run()
