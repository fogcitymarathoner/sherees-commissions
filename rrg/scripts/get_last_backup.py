import os
import argparse

from flask_script import Manager
from flask import Flask
from rrg.xml_helpers import download_last_database_backup

parser = argparse.ArgumentParser(description='RRG Get Last Backup')
parser.add_argument('--db-backups-dir', help='database backups directory', default='/php-apps/db_backups/')

parser.add_argument('--s3-folder',  help='S3 Folder', default='')
parser.add_argument('--bucket-name', required=True, help='Bucket Name', default='php-apps-cluster')
parser.add_argument('--aws-access-key-id', required=True, help='AWS_ACCESS_KEY_ID', default='rrg')
parser.add_argument('--aws-secret-access-key', required=True, help='AWS_SECRET_ACCESS_KEY_ID', default='deadbeef')
parser.add_argument('--backup-aging-time', help='delete backups older than backup-aging-time', default=30)

parser.add_argument('database', help='database name')

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


def get_last_db_backup_ep():
    """
    download last project db backup from S3
    """
    args = parser.parse_args()
    args.pat = "[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]-[0-9][0-9]-[0-9][0-9]-[0-9][0-9]-%s.sql.bz2" % args.database
    download_last_database_backup(
        args.aws_access_key_id, args.aws_secret_access_key, args.bucket_name, args.project_name, args.db_backups_dir)


manager = Manager(app)


@manager.option('-d', '--db-backups-dir', help='directory to zip up database dumps', required=True)
@manager.option('-p', '--project-name', dest='project_name', required=True)
def get_last_db_backup(project_name, aws_access_key_id, aws_secret_access_key, bucket_name, db_backups_dir):
    download_last_database_backup(aws_access_key_id, aws_secret_access_key, bucket_name, project_name, db_backups_dir)


if __name__ == "__main__":
    manager.run()
