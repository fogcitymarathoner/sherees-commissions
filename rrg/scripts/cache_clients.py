import os
import argparse
from keyczar import keyczar

from flask_script import Manager
from flask import Flask
from rrg.billing import cache_non_date_parsed as routine
from rrg.models import session_maker
from rrg.models import Client

parser = argparse.ArgumentParser(description='RRG Clients')

parser.add_argument(
    '--datadir', required=True, help='datadir dir', default='/php-apps/cake.rocketsredglare.com/rrg/data/')

parser.add_argument(
    '--keyczardir', required=True,
    help='dir of encryption keys generated by keyczart',
    default='/.keyczar')
parser.add_argument('--db-user', required=True, help='database user', default='marcdba')
parser.add_argument('--mysql-host', required=True, help='database host - MYSQL_PORT_3306_TCP_ADDR', default='marcdba')
parser.add_argument('--mysql-port', required=True, help='database port - MYSQL_PORT_3306_TCP_PORT', default=3306)
parser.add_argument('--db', required=True, help='database name', default='rrg')
parser.add_argument('--db-pass', required=True, help='database pw', default='deadbeef')

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


def cache_clients():
    """
    replaces cake cache_clients
    :param data_dir:
    :return:
    """
    args = parser.parse_args()
    session = session_maker(args)
    crypter = keyczar.Crypter.Read(args.keyczardir)
    print('Caching Clients %s into %s' % (args.db, os.path.join(args.datadir, 'clients')))
    routine(session, os.path.join(args.datadir, 'clients'), Client, crypter)
    session.commit()
