import argparse
from rrg.archive import employee
from rrg.renderers import format_employee

parser = argparse.ArgumentParser(description='RRG Archived Employee')

parser.add_argument('id', type=int, help='id from cached-employees report')
parser.add_argument('--datadir', required=True, help='datadir dir with ar.xml',
    default='/php-apps/cake.rocketsredglare.com/rrg/data/')


def cached_employee():
    """
    prints selected archived employee
    :param data_dir:
    :return:
    """
    args = parser.parse_args()
    print('Archived Employee in %s' % args.datadir)
    employee_dict = employee(args.id, args.datadir)
    print format_employee(employee_dict)
