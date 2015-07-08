#!/usr/bin/env python
# coding: utf-8

import cPickle as pickle
import csv
import os
import os.path
import pinyin
import re
import sys

import HTMLParser

ITEM_INTERNAL_ID                    = 0
ITEM_DISTRICT                       = 1
ITEM_COMMUNITY                      = 2
ITEM_NAME                           = 3
ITEM_ADDRESS                        = 4
ITEM_DEVELOPER                      = 5
ITEM_PROPERTY_MANAGEMENT_COMPANY    = 6
ITEM_PROPERTY_MANAGEMENT_TYPE       = 7
ITEM_PROPERTY_MANAGEMENT_FEE        = 8
ITEM_TOTAL_FLOOR_AREA               = 9
ITEM_TOTAL_HOUSEHOLDS               = 10
ITEM_TOTAL_SOURCE_SALE              = 11
ITEM_TOTAL_SOURCE_RENT              = 12
ITEM_BUILT_AGE                      = 13
ITEM_PLOT_RATIO                     = 14
ITEM_RENT_RATIO                     = 15
ITEM_PARKING                        = 16
ITEM_GREEN_COVERAGE                 = 17
ITEM_AVERAGE_PRICE                  = 18
ITEM_COMMENT                        = 19
ITEM_COUNT                          = 20

class MyMainParser(HTMLParser.HTMLParser):
    def __init__(self):
        HTMLParser.HTMLParser.__init__(self)

        self.dl = False
        self.dl_comm_l_detail = False
        self.dl_comm_r_detail = False
        self.dd_index = -1
        self.dd = False

        self.em_comm_avg_price = False

        self.div_desc_cont = False

        self.result = [""] * ITEM_COUNT

    def _check_attribute(self, attr, attrs):
        for i in attrs:
            if i[0] == "class" and attr in i[1].split():
                return True
        return False

    def _set_result(self, index, data):
        data = data.replace("\r", " ")
        data = data.replace("\n", " ")
        self.result[index] = data.strip()

    def _get_result(self, index):
        return self.result[index]

    def handle_starttag(self, tag, attrs):

        if tag == "dl":
            self.dl = True

            if self._check_attribute("comm-l-detail", attrs):
                self.dl_comm_l_detail = True
                self.dd_index = -1

            if self._check_attribute("comm-r-detail", attrs):
                self.dl_comm_r_detail = True
                self.dd_index = -1

        if tag == "dd":
            if self.dl_comm_l_detail or self.dl_comm_r_detail:
                self.dd = True
                self.dd_index = self.dd_index + 1

        if tag == "em":
            if self._check_attribute("comm-avg-price", attrs):
                self.em_comm_avg_price = True

        if tag == "div":
            if self._check_attribute("desc-cont", attrs):
                self.div_desc_cont = True

    def handle_endtag(self, tag):
        if self.dl:
            if tag == "dl":
                self.dl = False
                self.dl_comm_l_detail = False

        if self.dd:
            if tag == "dd":
                self.dd = False

        if self.em_comm_avg_price:
            if tag == "em":
                self.em_comm_avg_price = False

        if self.div_desc_cont:
            if tag == "div":
                self.div_desc_cont = False

    def handle_data(self, data):
        t = data.strip()
        if len(t) == 0:
            return

        if self.dd:
            if self.dl_comm_l_detail:
                if self.dd_index == 0:
                    self._set_result(ITEM_NAME, t)
                elif self.dd_index == 1:
                    if len(self._get_result(ITEM_DISTRICT)) == 0:
                        self._set_result(ITEM_DISTRICT, t)
                    else:
                        self._set_result(ITEM_COMMUNITY, t)
                elif self.dd_index == 2:
                    self._set_result(ITEM_ADDRESS, t)
                elif self.dd_index == 3:
                    self._set_result(ITEM_DEVELOPER, t)
                elif self.dd_index == 4:
                    self._set_result(ITEM_PROPERTY_MANAGEMENT_COMPANY, t)
                elif self.dd_index == 5:
                    self._set_result(ITEM_PROPERTY_MANAGEMENT_TYPE, t)
                elif self.dd_index == 6:
                    self._set_result(ITEM_PROPERTY_MANAGEMENT_FEE, t)

            if self.dl_comm_r_detail:
                if self.dd_index == 0:
                    self._set_result(ITEM_TOTAL_FLOOR_AREA, t)
                elif self.dd_index == 1:
                    self._set_result(ITEM_TOTAL_HOUSEHOLDS, t)
                elif self.dd_index == 2:
                    self._set_result(ITEM_BUILT_AGE, t)
                elif self.dd_index == 3:
                    self._set_result(ITEM_PLOT_RATIO, t)
                elif self.dd_index == 4:
                    self._set_result(ITEM_RENT_RATIO, t)
                elif self.dd_index == 5:
                    self._set_result(ITEM_PARKING, t)
                elif self.dd_index == 6:
                    self._set_result(ITEM_GREEN_COVERAGE, t)

        if self.em_comm_avg_price:
            self._set_result(ITEM_AVERAGE_PRICE, t)

        if self.div_desc_cont:
            self._set_result(ITEM_COMMENT, t)

class MySaleParser(HTMLParser.HTMLParser):
    def __init__(self):
        HTMLParser.HTMLParser.__init__(self)

        self.div_m_sortby = False
        self.strong = False

        self.result = ""

    def handle_starttag(self, tag, attrs):

        if tag == "div":
            if ("class", "m-sortby") in attrs:
                self.div_m_sortby = True

        elif tag == "strong":
            if self.div_m_sortby:
                self.strong = True

    def handle_endtag(self, tag):

        if self.strong:
            if tag == "strong":
                self.strong = False

        if self.div_m_sortby:
            if tag == "div":
                self.div_m_sortby = False

    def handle_data(self, data):

        if self.strong:
            self.result = data.strip()

def get_info(filename, parser):

    with open(filename) as myfile:
        data = myfile.read()

    #data = data.replace(r"&nbsp;", "")

    parser.feed(data)
    parser.close()
    return parser.result

def get_main_info(filename):
    p = MyMainParser()
    info = get_info(filename, p)

    # We only need the currency
    t = info[ITEM_PROPERTY_MANAGEMENT_FEE]
    m = re.findall(r"[\d.]+", t)
    if len(m) != 0:
        info[ITEM_PROPERTY_MANAGEMENT_FEE] = m[0]

    # We only need the number
    t = info[ITEM_TOTAL_FLOOR_AREA]
    m = re.findall(r"\d+", t)
    if len(m) != 0:
        info[ITEM_TOTAL_FLOOR_AREA] = m[0]

    t = info[ITEM_TOTAL_HOUSEHOLDS]
    m = re.findall(r"\d+", t)
    if len(m) != 0:
        info[ITEM_TOTAL_HOUSEHOLDS] = m[0]

    # We only need the percentage
    t = info[ITEM_GREEN_COVERAGE]
    m = re.findall(r"[\d.%]+", t)
    if len(m) != 0:
        info[ITEM_GREEN_COVERAGE] = m[0]

    return info

def get_sale_info(filename):
    p = MySaleParser()
    result = get_info(filename, p)
    if len(result) == 0:
        result = "0"
    return result

def get_rent_info(filename):

    # FIXME: xx
    p = MySaleParser()
    result = get_info(filename, p)
    if len(result) == 0:
        result = "0"
    return result

def save_to_file(info):

    # Dump the object to data
    data = pickle.dumps(info, pickle.HIGHEST_PROTOCOL)

    # Write the string to the file
    f = open("result.pickle", "wb")
    f.write(data)
    f.close()

def load_from_file():

    # Read the file.
    f = open("result.pickle", "rb")
    data = f.read()
    f.close()

    # Read the object from data
    return pickle.loads(data)

def write_to_csv(filename, data):
    fd = open(filename, "wb")
    writer = csv.writer(fd, delimiter="\t")

    for row in data:
        writer.writerow(row)
    fd.close()

def parse_html():
    result = []
    n = 0

    for root, dirs, files in os.walk("cm"):
        for filename in files:
            if filename.endswith(".html"):

                m = re.findall(r"cm\d+.html", filename)
                if len(m) > 0:

                    # Get main info
                    t = get_main_info(os.path.join(root, filename))

                    m = re.findall(r"\d+", filename)
                    t[ITEM_INTERNAL_ID] = m[0]

                    # Get sale info
                    t[ITEM_TOTAL_SOURCE_SALE] = get_sale_info( \
                            os.path.join(root, filename[:-5] + "_sale.html"))

                    # Get rent info
                    t[ITEM_TOTAL_SOURCE_RENT] = get_rent_info( \
                            os.path.join(root, filename[:-5] + "_rent.html"))

                    # Calculate the rent ratio
                    sale = int(t[ITEM_TOTAL_SOURCE_SALE])
                    rent = int(t[ITEM_TOTAL_SOURCE_RENT])
                    if rent == 0:
                        rent_ratio = 0.0
                    else:
                        if sale == 0:
                            rent_ratio = 80.0
                        else:
                            rent_ratio = 100.0 * rent / (rent + sale)
                            if rent_ratio > 80.0:
                                rent_ratio = 80.0
                    t[ITEM_RENT_RATIO] = "%d%%" % int(rent_ratio)

                    # Append the result
                    result.append(t)

                    # Print the progress
                    n = n + 1
                    sys.stdout.write("Processing %d / %d ...\r" % (n, len(files) / 3))

    print "\r\n"

    save_to_file(result)

    print "Done!"

def cmp_info(x, y):
    x0 = pinyin.get(x[ITEM_DISTRICT])
    y0 = pinyin.get(y[ITEM_DISTRICT])

    x1 = pinyin.get(x[ITEM_COMMUNITY])
    y1 = pinyin.get(y[ITEM_COMMUNITY])

    x2 = pinyin.get(x[ITEM_NAME])
    y2 = pinyin.get(y[ITEM_NAME])

    if len(x1) == 0:
        x1 = "zz"
    if len(y1) == 0:
        y1 = "zz"

    if len(x2) == 0:
        x2 = "zz"
    if len(y2) == 0:
        y2 = "zz"

    if x0 > y0:
        return -1
    elif x0 < y0:
        return 1
    else:
        if x1 < y1:
            return -1
        elif x1 > y1:
            return 1
        else:
            if x2 < y2:
                return -1
            elif x2 > y2:
                return 1
            else:
                return 0

def main():

    # ==========
    # Step 1
    # ==========

    #parse_html()

    # ==========
    # Step 2
    # ==========

    # Loop the items
    result = load_from_file()
    t0 = []
    t1 = []
    for i in result:
        if len(i[ITEM_COMMUNITY].strip()) != 0:
            # The items we want
            t0.append(i)
        else:
            # The items that have no community name
            t1.append(i)

    # But we still need the items whose names are new
    found = 0
    t2 = []
    for i in t1:
        for j in t0:
            if i[ITEM_NAME] == j[ITEM_NAME]:
                found = 1
        if found == 0:
            t2.append(i)
        else:
            found = 0

    t0.extend(t2)

    # Sort the items by 'cmp_info'
    t0.sort(cmp=cmp_info)

    # Write the items to file
    write_to_csv("result.csv", t0)
    write_to_csv("empty.csv", t1)

    print "Done!"

if __name__ == "__main__":
    main()
