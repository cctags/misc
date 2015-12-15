#!/usr/bin/env python

import sys
from twill.commands import *


def test_twill(email, passwd):
    go(r"https://tudouvpn.com/login.php")
    fv(1, "email", email)
    fv(1, "pass", passwd)
    submit('0')
    go(r"https://www.tudouvpn.com/daily.php")
    show()


def main():
    if len(sys.argv) < 3:
        print "\n" \
              "Usage:\n" \
              "    %s <email> <passwd>\n\n" % (sys.argv[0])
        sys.exit(-1)

    test_twill(sys.argv[1], sys.argv[2])

if __name__ == "__main__":
    main()
