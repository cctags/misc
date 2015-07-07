#!/usr/bin/env python
# coding: utf-8

import os
import re
import subprocess

url=r"http://www1.sample.com/sub"

# NOTE: until now we have to run this on win32 machine.
def download_p():
    for i in range(1, 3234):
        u = r"wget -c -nc -t 0 %s/W0QQpZ%d -O p/p%08d.html" % (url, i, i)
        p = subprocess.Popen(u.split())
        p.wait()

def parse_cm_from_p():
    com = []

    for i in range(1, 3234):

        print("Parsing %d / 3233 .." % (i))

        filename = r"p/p%08d.html" % (i)
        with open (filename, "r") as myfile:
            data = myfile.read()
        m = re.findall(r"%s/view/\d+" % (url), data)

        for t in m:
            if t not in com:
                com.append(t)

    p = open(r"p/p.txt", "wb")
    for i in com:
        p.write(i.strip() + os.linesep)
    p.close()
    print "Write file 'p/p.txt' OK!"

def download_cm():
    for line in open(r"p/p.txt"):
        u = line.strip()

        id = u[33:]
        while len(id) < 8:
            id = '0' + id

        u = r"wget -c -t 0 %s/ -O cm/cm%s.html" % (u, id)
        p = subprocess.Popen(u)
        p.wait()

def main():
    download_p()
    parse_cm_from_p()
    download_cm()

if __name__ == "__main__":
    main()
