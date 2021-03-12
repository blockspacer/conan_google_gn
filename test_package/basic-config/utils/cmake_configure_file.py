#!/usr/bin/env python3
# coding: utf8

__doc__ = ("Substitutes variable values referenced as @VAR@ or ${VAR} in the "
           "input file content. Each variable reference will be replaced with"
           " the current value of the variable, or the empty string if the "
           "variable is not defined.")

__version__ = '0.1'
__author__ = 'Matthieu Longo'


import argparse
import logging
import os
import pprint
import re
import sys

try:
    import coloredlogs
    coloredlogs.DEFAULT_LOG_FORMAT = '[%(levelname)s] %(message)s'
    # If you don't want to see log messages from libraries, you can pass a
    # specific logger object to the install() function. In this case only log
    # messages originating from that logger will show up on the terminal.
    coloredlogs.install(level='DEBUG', logger=logging.getLogger())
except ImportError:
    pass


class VariablesReplacer(object):
    """
        Replace variables referenced as @VAR@ or ${VAR} in a string
    """

    __CMAKE_VAR_SYNTAX = r'@(\w+)@'
    __DOLLAR_VAR_SYNTAX = r'\${(\w+)}'

    def __init__(self, variables, ignore_dollar_syntax=False):
        self.__variables = variables
        self.__ignore_dollar_syntax = ignore_dollar_syntax
        if ignore_dollar_syntax:
            self.__prog = re.compile(self.__CMAKE_VAR_SYNTAX)
        else:
            pattern = r"{}|{}".format(self.__CMAKE_VAR_SYNTAX, self.__DOLLAR_VAR_SYNTAX)
            self.__prog = re.compile(pattern)

    def __call__(self, s):
        def varrepl(matchobj):
            if self.__ignore_dollar_syntax:
                var_name = matchobj.group(1)
            else:
                var_name = matchobj.group(1) if matchobj.group(1) else matchobj.group(2)
            return self.__variables[var_name] if var_name in self.__variables.keys() else ""
        return self.__prog.sub(repl=varrepl, string=s)


def run(args):
    with open(args.input, 'r') as infile:
        def process(input_fd, output_fd):
            replace_vars = VariablesReplacer(variables=args.variables,
                                             ignore_dollar_syntax=args.ignore_dollar_syntax)
            for line in input_fd:
                output_fd.write(replace_vars(line))

        if args.output:
            with open(args.output, 'w') as outfile:
                process(infile, outfile)
        else:
            process(infile, sys.stdout)
    return 0


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

    def check_variable(s):
        """
            Check the pattern of variables in argument
        """
        if not re.match(pattern=r'\w+=\w', string=s):
            msg = "{} is not a valid value for a variable (example: VAR1=Value1)".format(s)
            logging.error(msg)
            raise ValueError(msg)
        return s

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-i', '--input', metavar='INFILE',
                        required=True,
                        type=check_path,
                        help="Input file containing variables to replace. The"
                             " input path must be a file, not a directory.")
    parser.add_argument('-o', '--output', metavar='OUTFILE',
                        help="Output file. If the path names an existing directory"
                             " the output file is placed in that directory with the"
                             " same file name as the input file."
                             " By default, the result is printed in the standard output.")
    parser.add_argument('-d', '--debug',
                        action='store_true',
                        help='Print debug information')
    parser.add_argument('--ignore-dollar-syntax',
                        action='store_true',
                        help="Restrict variable replacement to references of the"
                             " form @VAR@. This is useful for configuring scripts"
                             " that use ${VAR} syntax.")
    parser.add_argument('variables', metavar='VARS', nargs='*',
                        type=check_variable,
                        help="Pair of variable's name and variable's value"
                             " (example: VAR1=Value1 VAR2=Value2). No variable means"
                             " an empty dictionnary and hence variables will be "
                             "replaced by an empty string.")

    args = parser.parse_args()

    args.variables = dict(map(lambda s: tuple(s.split('=')), args.variables))
    if args.output:
        if os.path.isdir(args.output):
            args.output = os.path.join(args.output, os.path.basename(args.input) + '.out')
        else:
            dirpath = os.path.dirname(args.output)
            if not os.path.isdir(dirpath) and len(dirpath) > 0:
                msg = "{path} does not exist".format(path=dirpath)
                raise ValueError(msg)
    return args


if __name__ == '__main__':
    try:
        args = parse_args()
        if args.debug:
            logging.getLogger().setLevel(logging.DEBUG)
            logging.debug("Arguments:\n%s", pprint.pformat(vars(args), indent=2))
        sys.exit(run(args))
    except Exception as e:
        logging.error(str(e))
        sys.exit(1)
