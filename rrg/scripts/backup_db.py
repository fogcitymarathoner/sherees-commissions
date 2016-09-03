
import argparse

from s3_mysql_backup.s3_mysql_backup import backup_db as s3_backup_db

parser = argparse.ArgumentParser(description='S3 DB Bzckup')

parser.add_argument('project', help='project name', choices=['rrg', 'biz'])
parser.add_argument('--db-backups-dir', required=True, help='database backups directory',
                    default='/php-apps/cake.rocketsredglare.com/rrg/data/backups/')

parser.add_argument('--db-user', required=True, help='database user', default='marcdba')
parser.add_argument('--project-name', required=True, help='Project Name', default='rrg')
parser.add_argument('--s3-folder', required=True, help='S3 Folder', default='rrg')
parser.add_argument('--bucket-name', required=True, help='Bucket Name', default='php-apps-cluster')
parser.add_argument('--aws-access-key-id', required=True, help='AWS_ACCESS_KEY_ID', default='rrg')
parser.add_argument('--aws-secret-access-key', required=True, help='AWS_SECRET_ACCESS_KEY_ID', default='deadbeef')
parser.add_argument('--backup-aging-time', help='delete backups older than backup-aging-time', default=30)
parser.add_argument('--db-user', required=True, help='database user', default='marcdba')
parser.add_argument('--mysql-host', required=True, help='database host - MYSQL_PORT_3306_TCP_ADDR', default='marcdba')
parser.add_argument('--mysql-port', help='database port - MYSQL_PORT_3306_TCP_PORT', default=3306)
parser.add_argument('--db-pass', required=True, help='database pw', default='deadbeef')


#
# Databases to backup
#
# dbs = ['biz', 'personal', 'rrg', 'coppermine']


def backup_db():
    """
    dumps databases into /backups, uploads to s3, deletes backups older than a month
    fab -f ./fabfile.py backup_dbs
    """

    args = parser.parse_args()

    s3_backup_db(args)
