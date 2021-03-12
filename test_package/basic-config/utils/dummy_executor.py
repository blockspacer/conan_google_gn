#!/usr/bin/env python3
# coding: utf8

__doc__ = """Launch the command specified in parameter with all the given arguments."""

__version__ = '0.1'
__author__ = 'Matthieu Longo'


import os
import sys
import subprocess
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


class SubprocessOutputReader(object):

    def __init__(self, stdout):
        if sys.version_info[0] > 2:
            self._raw_output = stdout.decode("utf-8")
        else:
            self._raw_output = stdout
        self._ios = StringIO(self._raw_output)

    def get(self, io_handler=None):
        if io_handler:
            return io_handler(self._ios)
        else:
            return list(map(lambda line: line.strip('\r\n'), self._ios.readlines()))


if __name__ == '__main__':
    cmd = sys.argv[1:]
    if len(cmd) == 0:
        print(__doc__)
    else:
        subprocess.run(cmd, check=True)