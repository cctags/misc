#!/usr/bin/env python

import cStringIO
import HTMLParser
import pycurl

class MyFundHTMLParse(HTMLParser.HTMLParser):

    def __init__(self):
        HTMLParser.HTMLParser.__init__(self)

        self.span = False
        self.span_fund_code = False
        self.span_fund_name = False
        self.span_premium_rate = False
        self.span_fund_value = False
        self.span_fund_valRan = False
        self.span_fund_valExt = False

        # Format: name, code, premium_rate, value, valRan, valExt
        self.result = [""] * 6

    def _check_attribute(self, attr, attrs):
        for i in attrs:
            if i[0] == "class" and attr in i[1].split():
                return True
        return False

    def _set_result(self, index, data):
        self.result[index] = data.strip()

    def handle_starttag(self, tag, attrs):
        if tag == "span":
            self.span = True
            if self._check_attribute("fund_code", attrs):
                self.span_fund_code = True
            if self._check_attribute("fund_name", attrs):
                self.span_fund_name = True
            if self._check_attribute("premium_rate", attrs):
                self.span_premium_rate = True
            if self._check_attribute("fund_value", attrs):
                self.span_fund_value = True
            if self._check_attribute("fund_valRan", attrs):
                self.span_fund_valRan = True
            if self._check_attribute("fund_valExt", attrs):
                self.span_fund_valExt = True

    def handle_endtag(self, tag):
        if self.span:
            if tag == "span":
                self.span = False
                self.span_fund_code = False
                self.span_fund_name = False
                self.span_premium_rate = False
                self.span_fund_value = False
                self.span_fund_valRan = False
                self.span_fund_valExt = False

    def handle_data(self, data):
        if self.span:
            if self.span_fund_code:
                self._set_result(0, data)
            if self.span_fund_name:
                self._set_result(1, data)
            if self.span_premium_rate:
                self._set_result(2, data)
            if self.span_fund_value:
                self._set_result(3, data)
            if self.span_fund_valRan:
                self._set_result(4, data)
            if self.span_fund_valExt:
                self._set_result(5, data)

class MyShHTMLParse(HTMLParser.HTMLParser):

    def __init__(self):
        HTMLParser.HTMLParser.__init__(self)

        self.h1 = False
        self.h1_j_stockName = False
        self.h1_j_stockName_strong = False

        self.span = False
        self.span_j_serialNum = False
        self.span_j_valRange = False
        self.span_j_valExtent = False
        self.span_stock_info_value = False
        self.span_stock_info_value_index = -1

        self.strong = False
        self.strong_j_stockCurValue = False

        # Format: name, code, premium_rate, value, valRan, valExt
        self.result = [""] * 6

    def _check_attribute(self, attr, attrs):
        for i in attrs:
            if i[0] == "class" and attr in i[1].split():
                return True
        return False

    def _set_result(self, index, data):
        self.result[index] = data.strip()

    def handle_starttag(self, tag, attrs):
        if tag == "h1":
            self.h1 = True

            if ("class", "j_stockName") in attrs:
                self.h1_j_stockName = True

        elif tag == "span":
            self.span = True

            if ("class", "j_serialNum") in attrs:
                self.span_j_serialNum = True

            if self._check_attribute("j_valRange", attrs):
                self.span_j_valRange = True

            if self._check_attribute("j_valExtent", attrs):
                self.span_j_valExtent = True

            if self._check_attribute("stock_info_value", attrs):
                self.span_stock_info_value_index = self.span_stock_info_value_index + 1
                if self.span_stock_info_value_index == 1:
                    self.span_stock_info_value = True

        elif tag == "strong":
            self.strong = True

            if ("class", "j_stockCurValue") in attrs:
                self.strong_j_stockCurValue = True

            if self.h1 and self.h1_j_stockName:
                self.h1_j_stockName_strong = True

    def handle_endtag(self, tag):
        if self.h1:
            if tag == "h1":
                self.h1 = False
                self.h1_j_stockName = False
                self.h1_j_stockName_strong = False

        if self.span:
            if tag == "span":
                self.span = False

                self.span_j_serialNum = False
                self.span_j_valRange = False
                self.span_j_valExtent = False
                self.span_stock_info_value = False

        if self.strong:
            if tag == "strong":
                self.strong = False
                self.strong_j_stockCurValue = False

                self.h1_j_stockName_strong = False

    def handle_data(self, data):
        if self.h1:
            if self.h1_j_stockName:
                if self.h1_j_stockName_strong:
                    self._set_result(1, data)

        if self.span:
            if self.span_j_serialNum:
                self._set_result(0, data)
            if self.span_j_valRange:
                self._set_result(4, data)
            if self.span_j_valExtent:
                self._set_result(5, data)
            if self.span_stock_info_value:
                self._set_result(2, data)

        if self.strong:
            if self.strong_j_stockCurValue:
                self._set_result(3, data)

def get_fund(code):

    # Create a buffer object.
    buf = cStringIO.StringIO()

    # Get the fund data.
    c = pycurl.Curl()
    c.setopt(c.URL, r"http://stocks.sina.cn/fund/?code=%s&vt=4" % (code))
    c.setopt(c.WRITEFUNCTION, buf.write)
    c.setopt(c.CONNECTTIMEOUT, 20)
    c.setopt(c.TIMEOUT, 20)
    c.perform()

    # Parse the data.
    p = MyFundHTMLParse()
    p.feed(buf.getvalue())
    ret = p.result
    p.close()

    # Now close the buffer object.
    buf.close()

    # Return the value
    return ret

def get_sh(code):

    # Create a buffer object.
    buf = cStringIO.StringIO()

    # Get the fund data.
    c = pycurl.Curl()
    c.setopt(c.URL, r"http://stocks.sina.cn/sh/?code=%s&vt=4" % (code))
    c.setopt(c.WRITEFUNCTION, buf.write)
    c.setopt(c.CONNECTTIMEOUT, 20)
    c.setopt(c.TIMEOUT, 20)
    c.perform()

    # Parse the data.
    p = MyShHTMLParse()
    p.feed(buf.getvalue())
    ret = p.result
    p.close()

    # Now close the buffer object.
    buf.close()

    # Calculate the current value
    if len(ret[3]) == 0:
        ret[3] = "%.2f" % (float(ret[2]) + float(ret[4]))

    # Return the value
    return ret
