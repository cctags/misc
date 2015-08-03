#!/usr/bin/env python

from __future__ import division

import random
import math

radius = 1


def _get_random():

    n = random.randint(1, 100000)
    f = n / 100000
    f = f * radius * 2 - radius

    return f


def main():

    n = 1000000

    hit = 0

    for i in xrange(1, n + 1):
        x = _get_random()
        y = _get_random()

        distance = math.sqrt(math.pow(x, 2) + math.pow(y, 2))

        if distance <= radius:
            hit = hit + 1

    print "result = %.16f" % (4.0 * hit / n)

if __name__ == "__main__":
    main()
