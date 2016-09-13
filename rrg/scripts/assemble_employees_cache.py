import argparse
from rrg.archive import cached_employees_collect_contracts as routine

parser = argparse.ArgumentParser(description='RRG Assemble Employees Cache')

parser.add_argument(
    '--datadir', required=True,
    help='employees dir',
    default='/php-apps/cake.rocketsredglare.com/rrg/data/employees/')

parser.add_argument(
    '--contracts-dir', required=True,
    help='contracts dir',
    default='/php-apps/cake.rocketsredglare.com/rrg/data/contracts/')


def assemble_employees_cache():
    """
    gathers contracts for employees
    :param data_dir:
    :return:
    """
    args = parser.parse_args()

    print('Assembling Employees in %s' % args.datadir)
    routine(args)
