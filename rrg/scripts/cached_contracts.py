import argparse
from rrg.archive import contracts as routine

parser = argparse.ArgumentParser(description='RRG Archived Contracts')

parser.add_argument(
    '--datadir', required=True,
    help='datadir dir with ar.xml',
    default='/php-apps/cake.rocketsredglare.com/rrg/data/employees/')


def cached_contracts():
    """
    prints list of archived contracts for selection
    :param data_dir:
    :return:
    """
    args = parser.parse_args()

    print('Archived Contracts in %s' % args.datadir)
    routine(args)
