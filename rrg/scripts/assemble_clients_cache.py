import argparse
from rrg.archive import cached_clients_collect_contracts as routine

parser = argparse.ArgumentParser(description='RRG Assemble Clients Cache')

parser.add_argument(
    '--datadir', required=True,
    help='clients dir',
    default='/php-apps/cake.rocketsredglare.com/rrg/data/clients/')

parser.add_argument(
    '--contracts-dir', required=True,
    help='contracts dir',
    default='/php-apps/cake.rocketsredglare.com/rrg/data/contracts/')


def assemble_clients_cache():
    """
    gathers contracts for clients
    :param data_dir:
    :return:
    """
    args = parser.parse_args()

    print('Assembling Clients in %s' % args.datadir)
    routine(args)
