import argparse
from s3_mysql_backup import download_last_db_backup

parser = argparse.ArgumentParser(description='RRG Get Last Backup')
parser.add_argument('--db-backups-dir', help='database backups directory', default='/php-apps/db_backups/')

parser.add_argument('--s3-folder',  help='S3 Folder', default='')
parser.add_argument('--bucket-name', required=True, help='Bucket Name', default='php-apps-cluster')
parser.add_argument('--aws-access-key-id', required=True, help='AWS_ACCESS_KEY_ID', default='rrg')
parser.add_argument('--aws-secret-access-key', required=True, help='AWS_SECRET_ACCESS_KEY_ID', default='deadbeef')
parser.add_argument('--backup-aging-time', help='delete backups older than backup-aging-time', default=30)

parser.add_argument('database', help='database name')


def get_last_db_backup():
    """
    download last project db backup from S3
    """
    args = parser.parse_args()
    args.pat = "[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]-[0-9][0-9]-[0-9][0-9]-[0-9][0-9]-%s.sql.bz2" % args.database
    download_last_db_backup(args)
