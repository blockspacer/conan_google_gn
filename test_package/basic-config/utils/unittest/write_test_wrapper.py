#!/usr/bin/env python

import argparse
import json
import logging
import os
import re
import sys


def replace_vars(in_filename, out_filename, values):
    # Matches e.g. '${FOO}' or '@FOO@' and captures FOO in group 1 or 2.
    var_re = re.compile(r'\$\{([^}]*)\}|@([^@]*)@')

    def repl(m):
        key = m.group(1) or m.group(2)
        if key in values.keys():
            return values[key]
        else:
            return None

    with open(out_filename, 'w') as outfd:
        with open(in_filename, 'r') as infd:
            lines = infd.readlines()
            for line in lines:
                line = var_re.sub(repl, line)
                if line is not os.linesep:
                    logging.debug(line.rstrip())
                    outfd.write(line)


def run(args):
    values = {
        "TEST_CMD" : args.command
    }
    replace_vars(in_filename=args.input, out_filename=args.output, values=values)
    return 0


def parse_args():
    """
        Parse the script arguments
    """
    def check_path(path):
        """
            Paths checker
        """
        if not os.path.exists(path):
            raise ValueError("{path} does not exist".format(path=path))
        return path

    parser = argparse.ArgumentParser(description="""Generate a test wrapper""")
    parser.add_argument('-c', '--command', metavar='COMMAND',
                        required=True,
                        help="Test's command line")
    parser.add_argument('-d', '--debug',
                        action='store_true',
                        help='Print debug information')
    parser.add_argument('-f', '--input', metavar='INFILE',
                        required=True,
                        type=check_path,
                        help='Template file')
    parser.add_argument('-o', '--output', metavar='OUTFILE',
                        required=False,
                        help='Output file')
    args = parser.parse_args()
    if args.output is None:
        args.output = os.path.splitext(os.path.basename(args.input))[0]
    return args


def main():
    args = parse_args()
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug("arguments: {}".format( \
            json.dumps(vars(args), indent=2, sort_keys=True)))
    return run(args)


if __name__ == "__main__":
    sys.exit(main())