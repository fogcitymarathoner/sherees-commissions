import argparse
from rrg.sherees_commissions import sherees_notes_report

parser = argparse.ArgumentParser(description='RRG Sherees Notes Report')

parser.add_argument(
    '--format', required=True, choices=['plain', 'latex'],
    help='output format')


def notes():

    args = parser.parse_args()

    if args.format == 'plain':
        print(sherees_notes_report(format='plain'))
    elif args.format == 'latex':
        print(sherees_notes_report(format='latex'))
    print()
