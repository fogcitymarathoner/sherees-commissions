import os
import argparse
from rrg.archive import cached_employees_collect_contracts as routine

parser = argparse.ArgumentParser(description='RRG Assemble Employees Cache')
parser.add_argument(
    '--datadir', required=True, help='data root directory', default='/php-apps/cake.rocketsredglare.com/rrg/data/')


def assemble_employees_cache():
    """
    gathers contracts for employees
    :param data_dir:
    :return:
    """
    args = parser.parse_args()
    print('Assembling Employees in %s' % os.path.join(args.datadir, 'employees'))
    routine(args.datadir)
