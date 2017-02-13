import argparse
import os
from flask_script import Manager
from flask import Flask
from rrg.models import session_maker
from rrg.jos_models import DownloadFile
from rrg.jos_models import DownloadBlob

parser = argparse.ArgumentParser(description='RRG Cache Clients AR')

parser.add_argument(
    '--datadir', required=True,
    help='datadir dir with ar.xml',
    default='./recovered-files/')

parser.add_argument('--db-user', required=True, help='database user',
                    default='marcdba')
parser.add_argument('--mysql-host', required=True,
                    help='database host - MYSQL_PORT_3306_TCP_ADDR',
                    default='marcdba')
parser.add_argument('--mysql-port', required=True,
                    help='database port - MYSQL_PORT_3306_TCP_PORT',
                    default=3306)
parser.add_argument('--db', required=True, help='d', default='rrgjos')
parser.add_argument('--db-pass', required=True, help='database pw',
                    default='deadbeef')

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


def recover_joomla_documents_ep():
    """
    recovers vintage files from joomla blob records
    :param datadir:
    :return:
    """
    args = parser.parse_args()
    session = session_maker(args.db_user, args.db_pass, args.mysql_host, args.mysql_port, args.db)
    print('Recover Joomla Files')
    all_files = session.query(DownloadFile).filter(DownloadFile.isblob == 1)
    for f in all_files:
        print(f)
        chunks = session.query(DownloadBlob).filter(DownloadBlob.file == f).order_by(DownloadBlob.chunkid)
        outfile = os.path.join(args.datadir, f.realname)
        for chunk in chunks:
            print(chunk)
            with open(outfile, 'w') as fh:
                fh.write(chunk.datachunk)
        print('Wrote file %s' % outfile)


manager = Manager(app)


def recover_joomla_documents():
    session = session_maker(
        app.config['MYSQL_USER'], app.config['MYSQL_PASS'], app.config['MYSQL_SERVER_PORT_3306_TCP_ADDR'],
        app.config['MYSQL_SERVER_PORT_3306_TCP_PORT'], app.config['DB'])
    print('Recover Joomla Files')
    all_files = session.query(DownloadFile).filter(DownloadFile.isblob == 1)
    for f in all_files:
        print(f)
        chunks = session.query(DownloadBlob).filter(DownloadBlob.file == f).order_by(DownloadBlob.chunkid)
        outfile = os.path.join(app.config['DATADIR'], f.realname)
        for chunk in chunks:
            print(chunk)
            with open(outfile, 'w') as fh:
                fh.write(chunk.datachunk)
        print('Wrote file %s' % outfile)


if __name__ == "__main__":
    manager.run()

