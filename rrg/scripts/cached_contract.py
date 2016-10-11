import argparse
from rrg.archive import contract as routine

parser = argparse.ArgumentParser(description='RRG Archived Contract')

parser.add_argument('id', type=int, help='id from cached-contracts report')
parser.add_argument(
    '--datadir', required=True,
    help='datadir dir with ar.xml',
    default='/php-apps/cake.rocketsredglare.com/rrg/data/contracts/')


def cached_contract():
    """
    prints selected archived contract
    :param data_dir:
    :return:
    """
    args = parser.parse_args()

    print('Archived Contract in %s' % args.datadir)
    routine(args.datadir, args.id)
