#!/usr/bin/env python
# encoding: utf-8

import csv
import os
import os.path
import sys

import HTMLParser

class MyHTMLParser(HTMLParser.HTMLParser):
    def __init__(self):
        HTMLParser.HTMLParser.__init__(self)
        self.div_class__com_main = False
        self.div_class__c_r = False
        self.div_class__comm_intro = False
        self.span = False
        self.h1_class__t = False
        self.result = []

    def handle_starttag(self, tag, attrs):
        if tag == "div":
            if ("class", "com_main") in attrs:
                self.div_class__com_main = True
            elif ("class", "c_r") in attrs:
                self.div_class__c_r = True
            elif ("class", "comm-intro") in attrs:
                self.div_class__comm_intro = True
        elif tag == "h1":
            if self.div_class__com_main:
                if ("class", "t") in attrs:
                    self.h1_class__t = True
        elif tag == "span":
            if self.div_class__c_r:
                self.span = True

    def handle_endtag(self, tag):
        if self.h1_class__t:
            if tag == "h1":
                self.h1_class__t = False
        if self.div_class__com_main:
            if tag == "div":
                self.div_class__com_main = False
        if self.div_class__c_r:
            if tag == "div":
                self.div_class__c_r = False
                self.span = False
        if self.div_class__comm_intro:
            if tag == "div":
                self.div_class__comm_intro = False

    def handle_data(self, data):
        if self.div_class__com_main and self.h1_class__t:
            #print "o name:      ", data.strip()
            self.result.append(data.strip())

        if self.div_class__c_r:
            if self.span:
                t = data.strip()
                if len(t) != 0:
                    if t.startswith(r"总户数："):
                        last = len(t)
                        if t.endswith(r"户"):
                            last = t.rfind(r"户")
                        if last >= 0:
                            #print "o house:     ", t[len(r"总户数："):last]
                            self.result.append(t[len(r"总户数："):last])
                        else:
                            #print "o house:     ", t[len(r"总户数："):]
                            self.result.append(t[len(r"总户数："):])
                    elif t.startswith(r"停车位："):
                        #print "o parking:   ", t[len(r"停车位："):]
                        self.result.append(t[len(r"停车位："):])
                    elif t.startswith(r"竣工时间："):
                        #print "o complete:  ", t[len(r"竣工时间："):]
                        self.result.append(t[len(r"竣工时间："):])

        if self.div_class__comm_intro:
            t = data.strip()
            if len(t) != 0:
                i1 = t.find(r"具体地址")
                if i1 >= 0:
                    i1 += len(r"具体地址")
                else:
                    i1 = 0
                i2 = t.find(r"，该小区是")
                if i2 < 0:
                    i2 = len(t)
                if i1 == i2:
                    i1 = 0
                    i2 = len(t)
                #print "o Address:   ", t[i1:i2]
                self.result.append(t[i1:i2])

                #print "o Comment:   ", t
                self.result.append(t)

def get_info(filename):
    with open(filename) as myfile:
        data = myfile.read()

    data = data.replace(r"&nbsp;", "")

    p = MyHTMLParser()
    p.feed(data)
    p.close()
    return p.result

def write_to_csv(data):
    fd = open("result.csv", "wb")
    writer = csv.writer(fd, delimiter="\t")
    for row in data:
        writer.writerow(row)
    fd.close()

def main():
    result = []
    n = 0

    for root, dirs, files in os.walk("cm"):
        for filename in files:
            if filename.endswith(".html"):
                result.append(get_info(os.path.join(root, filename)))
                n = n + 1
                sys.stdout.write("Processing %d / %d ...\r" % (n, len(files)))

    write_to_csv(result)

    print "\r\nDone!"

if __name__ == "__main__":
    main()
