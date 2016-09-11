import argparse
from rrg.archive import employees as routine

parser = argparse.ArgumentParser(description='RRG Archived Employees')

parser.add_argument(
    '--datadir', required=True,
    help='datadir dir with ar.xml',
    default='/php-apps/cake.rocketsredglare.com/rrg/data/employees/')


def cached_employees():
    """
    prints list of archived employees for selection
    :param data_dir:
    :return:
    """
    args = parser.parse_args()

    print('Archived Employees in %s' % args.datadir)
    routine(args)
