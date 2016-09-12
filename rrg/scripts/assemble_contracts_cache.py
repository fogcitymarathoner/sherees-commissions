import argparse
from rrg.archive import cached_contracts_collect_invoices_and_items as routine

parser = argparse.ArgumentParser(description='RRG Assemble Contracts Cache')

parser.add_argument(
    '--datadir', required=True,
    help='contracts dir',
    default='/php-apps/cake.rocketsredglare.com/rrg/data/contracts/')

parser.add_argument(
    '--invoices-dir', required=True,
    help='invoices dir',
    default='/php-apps/cake.rocketsredglare.com/rrg/data/transactions/invoices/')


parser.add_argument(
    '--contract-items-dir', required=True,
    help='contract items dir',
    default='/php-apps/cake.rocketsredglare.com/rrg/data/contracts/contracts_items/')


def assemble_contracts_cache():
    """
    gathers contract items and invoices for contracts
    :param data_dir:
    :return:
    """
    args = parser.parse_args()

    print('Assembling Contracts in %s' % args.datadir)
    routine(args)
