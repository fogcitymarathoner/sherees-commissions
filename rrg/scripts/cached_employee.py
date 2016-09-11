import argparse
from rrg.archive import employee as routine

parser = argparse.ArgumentParser(description='RRG Archived Employees')

parser.add_argument('id', type=int, help='id from cached-employees report')
parser.add_argument(
    '--datadir', required=True,
    help='datadir dir with ar.xml',
    default='/php-apps/cake.rocketsredglare.com/rrg/data/employees/')


def cached_employee():
    """
    prints selected archived employee
    :param data_dir:
    :return:
    """
    args = parser.parse_args()

    print('Archived Employee in %s' % args.datadir)
    routine(args)
