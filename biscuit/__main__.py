# coding=utf-8
from __future__ import absolute_import, division, print_function, \
    unicode_literals

import argparse
import sys
import yaml
import logging

from . import biscuit
from ._version import VERSION

RC_OK = 0
RC_NOPE = 1


def main(args=None):
    logging.basicConfig()
    args = parse_args(args)

    secrets = biscuit()
    secrets.update(yaml.safe_load(open(args.filename, "r")))
    print(secrets.get(args.name))

    return RC_OK


def parse_args(args):
    if args is None:
        args = sys.argv[1:]
    parser = argparse.ArgumentParser(
        prog='biscuitpy',
        description='Reads values from files created by Biscuit.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('filename', metavar='filename')
    parser.add_argument('name', metavar='name')
    parser.add_argument('--version',
                        action='version',
                        version=VERSION,
                        help='Display version number and exit.')
    args = parser.parse_args(args)
    return args


if __name__ == '__main__':
    status = main()
    sys.exit(status)
