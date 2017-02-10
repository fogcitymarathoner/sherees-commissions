import os
import argparse

from flask_script import Manager
from flask import Flask

from s3_mysql_backup.backup_dir import backup

parser = argparse.ArgumentParser(description='RRg Datadir Backup')

parser.add_argument(
    '--datadir',
    required=True, help='datadir dir with cached data', default='/php-apps/cake.rocketsredglare.com/rrg/data/')
parser.add_argument('--zip-backups-dir', help='backup directory', default='/php-apps/db_backups/')

parser.add_argument('--s3-folder',  help='S3 Folder', default='')
parser.add_argument('--bucket-name', required=True, help='Bucket Name', default='php-apps-cluster')
parser.add_argument('--aws-access-key-id', required=True, help='AWS_ACCESS_KEY_ID', default='xxx')
parser.add_argument('--aws-secret-access-key', required=True, help='AWS_SECRET_ACCESS_KEY_ID', default='deadbeef')
parser.add_argument('--backup-aging-time', help='delete backups older than backup-aging-time', default=30)

parser.add_argument('project', help='project name')

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


def backup_datadir():
    """
    zips into args.db_backups_dir and uploads to args.bucket_name/args.s3_folder
    fab -f ./fabfile.py backup_dbs
    """

    args = parser.parse_args()

    backup(
        args.datadir,
        args.aws_access_key_id,
        args.aws_secret_access_key_id,
        args.bucket_name,
        args.zip_backups_dir,
        args.zip_backups_dir, args.backup_aging_time, args.s3_folder, args.project)


manager = Manager(app)


@manager.option('-z', '--zip-backups-dir', help='dir to assemble zipfiles', required=True)
def backup_datadir_to_s3(zip_backups_dir):
    print('Assembling Clients in %s' % app.config['DATADIR'])
    backup_aging_time = 30
    project = 'rrg'
    backup(
        app.config['DATADIR'],
        app.config['AWS_ACCESS_KEY_ID'],
        app.config['AWS_SECRET_ACCESS_KEY_ID'],
        app.config['BUCKET_NAME'],
        zip_backups_dir, backup_aging_time, app.config['S3_FOLDER'], project)

if __name__ == "__main__":
    manager.run()

