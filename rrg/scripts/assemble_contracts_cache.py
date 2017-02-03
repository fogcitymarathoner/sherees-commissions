import os
import argparse
from rrg.archive import cached_contracts_collect_invoices_and_items as routine

parser = argparse.ArgumentParser(description='RRG Assemble Contracts Cache')
parser.add_argument(
    '--datadir', required=True, help='data root directory', default='/php-apps/cake.rocketsredglare.com/rrg/data/')


def assemble_contracts_cache():
    """
    gathers contract items and invoices for contracts
    :param data_dir:
    :return:
    """
    args = parser.parse_args()
    print('Assembling Contracts in %s' % os.path.join(args.datadir, 'contracts'))
    routine(args.datadir)
