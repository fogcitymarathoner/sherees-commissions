import argparse
from s3_mysql_backup import download_last_db_backup

parser = argparse.ArgumentParser(description='RRG Get Last Backup')


parser.add_argument('project', help='project name',
                    choices=['rrg', 'biz'])
parser.add_argument(
    '--db_backups_dir', required=True,
    help='datadir dir with ar.xml',
    default='backups')


def get_last_db_backup():
    """
    download last project db backup from S3
    """
    args = parser.parse_args()
    download_last_db_backup(
        db_backups_dir=args.db_backups_dir, project_name=args.project)
