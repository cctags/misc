import argparse
import glob
import os
import os.path
import re
import sys

def _parse_args():
    parser = argparse.ArgumentParser(description="Renames multiple files.")
    parser.add_argument("-v", "--verbose", action="store_true", help="print names of files successfully renamed")
    parser.add_argument("-n", "--no-act", action="store_true", help="show what files would have been renamed")
    parser.add_argument("-f", "--force", action="store_true", help="overwrite existing files")
    parser.add_argument("pattern", nargs=1)
    parser.add_argument("repl", nargs=1)
    parser.add_argument("file", nargs="+")
    return parser.parse_args()

def _panic(message, errno=-1):
    print os.linesep + "*ERROR*: " + message
    sys.exit(errno)

def main():

    # Parse the arguments
    args = _parse_args()

    pattern = args.pattern[0]
    repl = args.repl[0]

    overwritten = False

    # The pattern and the repl can't be same
    if pattern == repl:
        _panic("'pattern' and 'repl' are same.")

    old_files = []
    new_files = []

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
            overwritten = True

        # Update the list
        new_files.append(new)

    # Check if overwritten
    if not args.force:
        if overwritten:
            panic("overwritten.")

    # Loop all the files
    for old, new in zip(old_files, new_files):

        if args.verbose or args.no_act:
            print "'%s' -> '%s'" % (old, new)

        if old != new:
            if not args.no_act:
                os.rename(old, new)

if __name__ == "__main__":
    main()
