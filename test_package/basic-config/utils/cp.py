#! /usr/bin/env python3
# coding: utf8

__doc__ = """Copy files specified in parameter to a given location"""

__version__ = '0.1'
__author__ = 'Matthieu Longo'


import argparse
import logging
import os
import pathlib
import pprint
import sys
import shutil

try:
    import coloredlogs
    coloredlogs.DEFAULT_LOG_FORMAT = '[%(levelname)s] %(message)s'
    # If you don't want to see log messages from libraries, you can pass a
    # specific logger object to the install() function. In this case only log
    # messages originating from that logger will show up on the terminal.
    coloredlogs.install(level='DEBUG', logger=logging.getLogger())
except ImportError:
    pass


def parse_args():
    """
        Parse the script arguments
    """
    from argparse import ArgumentError

    def check_path(path):
        """
            Paths checker
        """
        if not os.path.exists(path):
            msg = "{path} does not exist".format(path=path)
            logging.error(msg)
            raise ValueError(msg)
        return path

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-d', '--debug',
                        action='store_true',
                        help='Print debug information')
    parser.add_argument('infile', nargs=1,
                        type=check_path,
                        help="File to copy")
    parser.add_argument('outfile', nargs=1,
                        help="Destination path of the file to copy")

    args = parser.parse_args()
    return args


def run(args):
    infile = args.infile[0]
    output = args.outfile[0]

    # Build the missing directories on the output path
    if not os.path.exists(output):
        output_dir = os.path.dirname(output)
        if not os.path.isdir(output_dir):
            logging.debug("mkdir -p {}".format(output_dir))
            pathlib.Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Copy the file
    if os.path.isdir(output):
        filename = os.path.basename(infile)
        if os.path.exists(os.path.join(output, filename)):
            logging.info("Overwriting destination: {}".format(os.path.join(output, filename)))
        shutil.copy(src=infile, dst=output)
    else:
        if os.path.exists(output):
            logging.info("Overwriting destination: {}".format(output))
        shutil.copyfile(src=infile, dst=output)
    return 0


if __name__ == '__main__':
    try:
        args = parse_args()
        if args.debug:
            logging.getLogger().setLevel(logging.DEBUG)
            logging.debug("Arguments:\n%s", pprint.pformat(vars(args), indent=2))
            logging.debug("Current directory: {}".format(os.getcwd()))
        sys.exit(run(args))
    except Exception as e:
        logging.error(str(e))
        sys.exit(1)
