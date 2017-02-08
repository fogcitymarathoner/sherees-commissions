import argparse
import os
import re

from flask_script import Manager
from flask import Flask
from s3_mysql_backup import mkdirs
from s3_mysql_backup.s3_mysql_backup import s3_key

parser = argparse.ArgumentParser(
    description='S3 Download DB Backups')

parser.add_argument('project', help='project name',choices=['rrg', 'biz'])
parser.add_argument('--db-backups-dir', required=True, help='database backups directory',
                    default='/php-apps/cake.rocketsredglare.com/rrg/data/backups/')

parser.add_argument('--db-user', required=True, help='database user', default='marcdba')
parser.add_argument('--project-name', required=True, help='Project Name', default='rrg')
parser.add_argument('--bucket-name', required=True, help='Bucket Name', default='php-apps-cluster')
parser.add_argument('--aws-access-key-id', required=True, help='AWS_ACCESS_KEY_ID', default='rrg')
parser.add_argument('--aws-secret-access-key', required=True, help='AWS_SECRET_ACCESS_KEY_ID', default='deadbeef')

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



def download_last_db_backup():
    """
    download last project db backup from S3
    """
    args = parser.parse_args()

    archive_file_extension = 'sql.bz2'
    if os.name == 'nt':
        raise NotImplementedError

    else:
        key, bucketlist = s3_key(**args)

        TARFILEPATTERN = "[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]-[0-9][0-9]-[0-9][0-9]-[0-9][0-9]-%s.%s" % \
                         (args.project_name, archive_file_extension)

        #
        # delete files over a month old, locally and on server
        #
        backup_list = []
        for f in bucketlist:
            parray = f.name.split('/')
            filename = parray[len(parray)-1]
            if re.match(TARFILEPATTERN, filename):
                farray = f.name.split('/')
                fname = farray[len(farray)-1]
                dstr = fname[0:19]

                fdate = dt.strptime(dstr, "%Y-%m-%d-%H-%M-%S")
                backup_list.append({'date': fdate, 'key': f})

        backup_list = sorted(
            backup_list, key=lambda k: k['date'], reverse=True)

        if len(backup_list) > 0:
            last_backup = backup_list[0]
            keyString = str(last_backup['key'].key)
            basename = os.path.basename(keyString)
            # check if file exists locally, if not: download it

            mkdirs(args.db_backups_dir)

            dest = os.path.join(args.db_backups_dir, basename)
            print('Downloading %s to %s' % (keyString, dest))
            if not os.path.exists(dest):
                with open(dest, 'wb') as f:
                    last_backup['key'].get_contents_to_file(f)
            return last_backup['key']
        else:
            print 'There is no S3 backup history for project %s' % args.project_name
            print 'In ANY Folder of bucket %s' % bucket_name

