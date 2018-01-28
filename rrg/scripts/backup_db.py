import os
import argparse

from flask_script import Manager
from flask import Flask

from s3_mysql_backup.backup_db import backup_db as s3_backup_db

parser = argparse.ArgumentParser(description='S3 DB Backup')

parser.add_argument('--db-backups-dir', help='database backups directory', default='/php-apps/db_backups/')

parser.add_argument('--s3-folder',  help='S3 Folder', default='')
parser.add_argument('--bucket-name', required=True, help='Bucket Name', default='php-apps-cluster')
parser.add_argument('--aws-access-key-id', required=True, help='AWS_ACCESS_KEY_ID', default='rrg')
parser.add_argument('--aws-secret-access-key', required=True, help='AWS_SECRET_ACCESS_KEY', default='deadbeef')
parser.add_argument('--backup-aging-time', help='delete backups older than backup-aging-time', default=30)
parser.add_argument('--mysql-host', required=True, help='database host - MYSQL_PORT_3306_TCP_ADDR', default='marcdba')
parser.add_argument('--mysql-port', help='database port - MYSQL_PORT_3306_TCP_PORT', default=3306)
parser.add_argument('--db-user', required=True, help='database user', default='marcdba')
parser.add_argument('--db-pass', required=True, help='database pw', default='deadbeef')

parser.add_argument('database', help='database name')

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


def backup_db_ep():
    """
    dumps databases into /backups, uploads to s3, deletes backups older than a month
    entrypoint
    rrg-backup-db --db-user root --bucket-name php-apps-cluster --aws-access-key-id dddddd --aws-secret-access-key ccccccc --mysql-host $MYSQL_SERVER_PORT_3306_TCP_ADDR --mysql-port $MYSQL_SERVER_PORT_3306_TCP_PORT --db-pass xxx $1
    """
    args = parser.parse_args()
    s3_backup_db(
        args.aws_access_key_id,
        args.aws_secret_access_key,
        args.aws_bucket,
        args.s3_folder,
        args.database,
        args.mysql_host,
        args.mysql_port,
        args.db_user,
        args.db_pass,
        args.db_backups_dir,
        args.backup_aging_time)


manager = Manager(app)


@manager.option('-f', '--s3_folder', help='destination folder on S3', required=True)
@manager.option('-d', '--db-backups-dir', help='directory to zip up database dumps', required=True)
@manager.option('-a', '--backup_aging_time', help='dont let backups get older than ...', default=30)
def backup_db(s3_folder, db_backups_dir, backup_aging_time):
    """
    backup_db.py backup_database -d /php-apps/db_backups/ -f mysql-db-backups
    """
    s3_backup_db(
        app.config['AWS_ACCESS_KEY_ID'],
        app.config['AWS_SECRET_ACCESS_KEY'],
        app.config['AWS_BUCKET'],
        s3_folder,
        app.config['DB'],
        app.config['MYSQL_SERVER_PORT_3306_TCP_ADDR'], 
        app.config['MYSQL_SERVER_PORT_3306_TCP_PORT'], 
        app.config['MYSQL_USER'], 
        app.config['MYSQL_PASS'], 
        db_backups_dir, 
        backup_aging_time)

if __name__ == "__main__":
    manager.run()
