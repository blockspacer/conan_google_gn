#!/usr/bin/env python3
# coding: utf8

__doc__ = ("Parse a file containing environment operations with the following format:"
           " 'name=\"VAR_IDENTIFIER\",op=\"(set|unset|prepend|append)\",value=\"string_value\"'."
           " It outputs a script allowing to execute any command with the environment"
           " previously specified.")

__version__ = '0.1'
__author__ = 'Matthieu Longo'


import argparse
from collections import namedtuple
import copy
import json
import logging
import os
import pprint
import re
import stat
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

    SUPPORTED_LANGUAGES = { "bash" }
    def check_language(s):
        """
            Check the pattern of variables in argument
        """
        if s not in SUPPORTED_LANGUAGES:
            msg = "{language} is not supported yet. Supported languages: {supported}".format(language=s, supported=SUPPORTED_LANGUAGES)
            logging.error(msg)
            raise ValueError(msg)
        return s

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-l', '--language', metavar='LANGUAGE',
                        required=False,
                        default="bash",
                        type=check_language,
                        help="Language that will be used to generate the script ("
                             "possible values: {}).".format(', '.join(SUPPORTED_LANGUAGES)))
    parser.add_argument('-e', '--env-ops', metavar='ENVFILE',
                        required=True,
                        type=check_path,
                        help="File containing environment operations.")
    parser.add_argument('-o', '--output', metavar='OUTFILE',
                        required=True,
                        help="Script path. On Unix, the rights {} will be applied "
                             " the script.".format(stat.filemode(ScriptWritter.UNIX_RIGHTS)))
    parser.add_argument('-d', '--debug',
                        action='store_true',
                        help='Print debug information')

    args = parser.parse_args()
    return args


EnvOperation = namedtuple('EnvOperation', ['name', 'op', 'value'])


class EnvOperationDecoder(object):

    __OPERATION_MATCHER = re.compile(r'''name="(\w+)",op="(\w+)",value="(([^"\\]|\\")*)"''')

    def __init__(self, operation):
        try:
            result = self.__OPERATION_MATCHER.match(operation)
            if not result:
                raise Exception("Validation failed")
            self._op = EnvOperation(name=result.group(1),
                                    op=result.group(2),
                                    value=result.group(3))
        except Exception as e:
            msg = "\"{}\" is not a valid environment operation".format(operation)
            raise ValueError(msg)

    def get(self):
        return self._op


class EnvOperationsMerger(object):

    def __init__(self):
        self._operations = dict()

    def reconcile(self, operation):
        if operation.name in self._operations.keys():
            current = self._operations[operation.name]
            if operation.op == "unset" or operation.op == "set" or "unset" in current.keys():
                self._operations[operation.name] = { operation.op: operation.value }
            elif "set" in current.keys():
                if operation.op == "prepend":
                    self._operations[operation.name]["set"] = os.pathsep.join([operation.value, current["set"]])
                else: # append
                    self._operations[operation.name]["set"] = os.pathsep.join([current["set"], operation.value])
            else: # append or prepend or both
                if operation.op in current.keys():
                    if operation.op == "prepend":
                        new_value = os.pathsep.join([operation.value, current["prepend"]])
                    else: # append
                        new_value = os.pathsep.join([current["append"], operation.value])
                    self._operations[operation.name][operation.op] = new_value
                else:
                    self._operations[operation.name][operation.op] = operation.value
        else:
            self._operations[operation.name] = { operation.op: operation.value }

    def get(self):
        return copy.deepcopy(self._operations)


class BashRenderer(object):

    @classmethod
    def render(cls, operations):
        from io import StringIO
        output = StringIO()
        output.write("#!/usr/bin/env bash\n")
        for varname, operation in operations.items():
            for op_type, value in operation.items():
                if op_type == "unset":
                    output.write("unset {varname}\n".format(varname=varname))
                elif op_type == "set":
                    output.write('export {varname}="{value}"\n'.format(varname=varname, value=value))
                elif op_type == "prepend":
                    output.write('export {varname}="{value}${{{varname}:+":${{{varname}}}"}}"\n'.format(varname=varname, value=value))
                elif op_type == "append":
                    output.write('export {varname}="${{{varname}:+"${{{varname}}}:"}}{value}"\n'.format(varname=varname, value=value))
        output.write('echo "${@}"\n')
        output.write("${@}\n")
        content = output.getvalue()
        output.close()
        return content


class ScriptWritter(object):
    UNIX_RIGHTS = stat.S_IFREG | stat.S_IRWXU | stat.S_IRWXG | stat.S_IROTH

    def __init__(self, operations):
        self._operations = operations

    def write(self, filepath, renderer):
        with open(filepath, 'w') as fd:
            fd.write(renderer.render(self._operations))
        os.chmod(filepath, self.UNIX_RIGHTS)


def run(args):
    merger = EnvOperationsMerger()
    with open(args.env_ops, 'r') as fd:
        for operation in fd.readlines():
            merger.reconcile(EnvOperationDecoder(operation).get())
        operations = merger.get()
        if args.language == "bash":
            renderer = BashRenderer
        ScriptWritter(operations).write(args.output, renderer)
    return 0


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
