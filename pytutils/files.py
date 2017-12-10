import os
import sys


def islurp(filename, mode='r', allow_stdin=True, expanduser=True, expandvars=True):
    """
    Read a file and yield each line.
    If filename is '-' and allow_stdin=True (default), read from stdin.
    """
    fh = None
    try:
        if filename == '-' and allow_stdin:
            fh = sys.stdin
        else:
            if expanduser:
                filename = os.path.expanduser(filename)
            if expandvars:
                filename = os.path.expandvars(filename)

            fh = open(filename, mode)

        while True:
            line = fh.readline()
            if line == '':  # EOF
                break
            yield line
    finally:
        if fh and fh != sys.stdin:
            fh.close()


slurp = islurp


def burp(filename, contents, mode='w', allow_stdout=True, expanduser=True, expandvars=True):
    """
    Write `contents` to `filename`.
    """
    if filename == '-' and allow_stdout:
        sys.stdout.write(contents)
    else:
        if expanduser:
            filename = os.path.expanduser(filename)
        if expandvars:
            filename = os.path.expandvars(filename)

        with open(filename, mode) as fh:
            fh.write(contents)
