import argparse
from rrg.archive import cached_contracts_collect_invoices_and_items as routine
from rrg.utils import contracts_dir

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
    print('Assembling Contracts in %s' % contracts_dir(args.datadir))
    routine(args.datadir)
