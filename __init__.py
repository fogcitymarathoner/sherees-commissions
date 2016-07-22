
import os
import time
from datetime import datetime as dt

from s3_mysql_backup import DIR_CREATE_TIME_FORMAT


def directory_date_dictionary(dir):
    """
    returns dictionary of a directory in (name: cdate} format
    :param dir:
    :return:
    """
    dirFileList = []
    for dirName, subdirList, fileList in os.walk(dir, topdown=False):
        if dir == dirName:
            for f in fileList:

                dirFileList.append(os.path.join(dirName, f))

    return {f: dt.strptime(time.ctime(os.path.getmtime(f)), DIR_CREATE_TIME_FORMAT) for f in dirFileList}


