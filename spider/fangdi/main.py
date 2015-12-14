#!/usr/bin/env python

import sys
from twill.commands import *


def test_twill(transactionid):
    go(r"http://202.109.79.211:8002/")
    fv(1, "transactionid", transactionid)
    submit('0')
    show()


def main():
    for i in sys.argv[1:]:
        test_twill(i)

if __name__ == "__main__":
    main()
