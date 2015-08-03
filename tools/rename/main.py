#!/usr/bin/env python

import argparse
import glob
import os
import os.path
import re
import sys


def _parse_args():
    parser = argparse.ArgumentParser(description="Renames multiple files.")
    parser.add_argument("-f", "--force", action="store_true",
                        help="overwrite existing files")
    parser.add_argument("-n", "--no-act", action="store_true",
                        help="show what files would have been renamed")
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="do not write anything to standard output")
    parser.add_argument("pattern", nargs=1)
    parser.add_argument("repl", nargs=1)
    parser.add_argument("file", nargs="+")
    return parser.parse_args()


def _panic(message, errno=-1):
    print os.linesep + "*ERROR*: " + message
    sys.exit(errno)


def _print_file_change(old_files, new_files, print_flags=None):

    if print_flags is None:
        print_flags = [True] * len(old_files)

    for old, new, flag in zip(old_files, new_files, print_flags):
        if flag:
            print "'%s' -> '%s'" % (old, new)


def main():

    # Parse the arguments
    args = _parse_args()

    pattern = args.pattern[0]
    repl = args.repl[0]

    # The pattern and the repl can't be same
    if pattern == repl:
        _panic("'pattern' and 'repl' are same.")

    old_files = []
    new_files = []
    overwritten_flags = []

    # Find all the files
    for pathname in args.file:
        for i in glob.glob(pathname):
            if i not in old_files:
                old_files.append(i)

    # Quit if file not found
    if len(old_files) == 0:
        _panic("file not found.")

    # Loop all the files
    for i in old_files:

        dir, filename = os.path.split(i)

        # Construct the new filenames
        new = re.sub(pattern, repl, filename)
        new = os.path.join(dir, new)

        # overwritten?
        if new in new_files:
            overwritten_flags[new_files.index(new)] = True
            overwritten_flags.append(True)
        else:
            overwritten_flags.append(False)

        # Update the list
        new_files.append(new)

    # no-act
    if args.no_act:
        _print_file_change(old_files, new_files)
        sys.exit(0)

    # Check if overwritten
    if not args.force:
        if True in overwritten_flags:
            _print_file_change(old_files, new_files, overwritten_flags)
            _panic("overwritten.")

    # Loop all the files
    change_flags = []

    for old, new in zip(old_files, new_files):

        if old != new:
            os.rename(old, new)
            change_flags.append(True)
        else:
            change_flags.append(False)

    if not args.quiet:
        _print_file_change(old_files, new_files, change_flags)
        print "\n%d file(s) have been renamed." % (change_flags.count(True))

if __name__ == "__main__":
    main()
