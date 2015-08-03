#!/usr/bin/python -B

import argparse
import colorama

import sina

program_version = "v0.0.1"


def _print_line(line, color=False):
    c0 = colorama.Fore.RESET
    if color:
        if "+" in line[5]:
            c0 = colorama.Fore.RED
        elif "-" in line[5]:
            c0 = colorama.Fore.GREEN

    c1 = colorama.Fore.RESET + colorama.Back.RESET + colorama.Style.RESET_ALL

    format_string = "%-8s\t%-20s\t%8s\t" + c0 + "%8s\t%8s\t%8s" + c1

    print(format_string % (line[0], line[1].decode("utf-8"), line[2],
                           line[3], line[4], line[5]))


def _parse_args():
    parser = argparse.ArgumentParser(
        description="Simple stock viewer. %s" % (program_version))
    parser.add_argument(
        "-t", "--type", help="specify the type", choices=("sh", "fund"))
    parser.set_defaults(type="sh")
    parser.add_argument(
        "-c", "--color", help="highlight the output (default off)", action="store_true")
    parser.add_argument("-v", "--version", action="version",
                        version=program_version)
    parser.add_argument("code", nargs=1, help="specify the code")
    return parser.parse_args()


def main():
    args = _parse_args()

    if args.type == "sh":
        f = sina.get_sh
    elif args.type == "fund":
        f = sina.get_fund

    assert(f is not None)

    t = f(args.code[0])
    _print_line(t, args.color)

if __name__ == "__main__":
    main()
