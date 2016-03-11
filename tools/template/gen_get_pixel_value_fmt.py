#!/usr/bin/env python

import sys

"""
Usage:
    app A8R8G8B8"
"""


def gen_get_header(text):
    print "void GetPixelValue_%s(gctUINT32 Value, gctUINT32 *R, gctUINT32 *G, gctUINT32 *B, gctUINT32 *A);" % (text)


def gen_set_header(text):
    print "gctUINT32 SetPixelValue_%s(gctUINT32 R, gctUINT32 G, gctUINT32 B, gctUINT32 A);" % (text)


def gen_get_func(text):
    component = text[::2]
    size = [int(i) for i in text[1::2]]

    width = []
    end = 0
    for i in size[::-1]:
        width.insert(0, [i + end - 1, end])
        end = width[0][0] + 1

    print "static void GetPixelValue_%s(gctUINT32 Value, gctUINT32 *R, gctUINT32 *G, gctUINT32 *B, gctUINT32 *A)" % (text)
    print "{"
    for i in range(len(component)):
        print "    *%s = gcmGETFIELD(Value, %d:%d);" % (component[i], width[i][0], width[i][1])
    if len(component) < 4:
        print "    *A = 0x100;"
    print "}"
    print ""


def gen_set_func(text):
    component = text[::2]
    size = [int(i) for i in text[1::2]]

    width = []
    end = 0
    for i in size[::-1]:
        width.insert(0, [i + end - 1, end])
        end = width[0][0] + 1

    print "static gctUINT32 SetPixelValue_%s(gctUINT32 R, gctUINT32 G, gctUINT32 B, gctUINT32 A)" % (text)
    print "{"
    print "    gctUINT32 value = 0;"
    print ""
    for i in range(len(component)):
        print "    value = gcmSETFIELD(value, %d:%d, %s);" % (width[i][0], width[i][1], component[i])
    print ""
    print "    return value;"
    print "}"
    print ""


def gen_switch(text):
    print "case gcvSURF_%s:" % (text)
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
