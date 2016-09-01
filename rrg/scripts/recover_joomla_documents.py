import argparse
import os
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


def recover_joomla_documents():
    """
    recovers vintage files from joomla blob records
    :param datadir:
    :return:
    """
    args = parser.parse_args()
    session = session_maker(args)

    print('Recover Joomla Files')

    all_files = session.query(DownloadFile).filter(DownloadFile.isblob == 1)
    for f in all_files:
        print(f)
        chunks = session.query(
            DownloadBlob).filter(DownloadBlob.file == f).order_by(
            DownloadBlob.chunkid)
        outfile = os.path.join(args.datadir, f.realname)
        for chunk in chunks:
            print(chunk)
            with open(outfile, 'w') as fh:
                fh.write(chunk.datachunk)
        print('Wrote file %s' % outfile)
