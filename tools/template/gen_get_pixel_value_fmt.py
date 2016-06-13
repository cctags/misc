#!/usr/bin/env python

import re
import sys

"""
Usage:
    app A8R8G8B8"
"""


def gen_get_header(text):
    print "void GetPixelValue_%s(unsigned int Value, unsigned int *R, unsigned int *G, unsigned int *B, unsigned int *A);" % (text)


def gen_set_header(text):
    print "unsigned int SetPixelValue_%s(unsigned int R, unsigned int G, unsigned int B, unsigned int A);" % (text)


def gen_get_func(text):
    groups = re.findall("[RGBAX]\d+", text)
    component = [i[0] for i in groups]
    size = [int(i[1:]) for i in groups]

    width = []
    end = 0
    for i in size[::-1]:
        width.insert(0, [i + end - 1, end])
        end = width[0][0] + 1

    print "static void GetPixelValue_%s(unsigned int Value, unsigned int *R, unsigned int *G, unsigned int *B, unsigned int *A)" % (text)
    print "{"

    for i in range(len(component)):
        if component[i] != 'X':
            print "    *%s = prefixmGETFIELD(Value, %d:%d);" % (component[i], width[i][0], width[i][1])

    if 'X' in component:
        print "    *A = 0x100;"

    print "}"
    print ""


def gen_set_func(text):
    groups = re.findall("[RGBAX]\d+", text)
    component = [i[0] for i in groups]
    size = [int(i[1:]) for i in groups]

    width = []
    end = 0
    for i in size[::-1]:
        width.insert(0, [i + end - 1, end])
        end = width[0][0] + 1

    print "static unsigned int SetPixelValue_%s(unsigned int R, unsigned int G, unsigned int B, unsigned int A)" % (text)
    print "{"
    print "    unsigned int value = 0;"
    print ""
    for i in range(len(component)):
        if component[i] != 'X':
            print "    value = prefixmSETFIELD(value, %d:%d, %s);" % (width[i][0], width[i][1], component[i])
    print ""
    print "    return value;"
    print "}"
    print ""


def gen_switch(text):
    print "case prefixvSURF_%s:" % (text)
    print "    m_GetPixelValueFunc = GetPixelValue_%s;" % (text)
    print "    m_SetPixelValueFunc = SetPixelValue_%s;" % (text)
    print "    break;"
    print


def main():
    for i in sys.argv[1:]:
        # gen_get_header(i)
        # gen_get_func(i)

        # gen_set_header(i)
        # gen_set_func(i)

        gen_switch(i)


if __name__ == "__main__":
    main()
