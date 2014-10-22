#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re

linkRE = re.compile('(?<=\[\[)\w*(?=[|\]])', re.UNICODE)
nameRe = re.compile('(?<=[|\[])\w+(?=\]\])', re.UNICODE)


def probeLink(s):
    """
    >>> probeLink('   abc')
    []
    >>> probeLink('   [[]]')
    [('', '')]
    >>> probeLink('   [[abc]]   [[abc|123]]  ')
    [('abc', 'abc'), ('abc', '123')]
    """
    ns = s.decode('utf8')
    return zip(linkRE.findall(ns), nameRe.findall(ns))


def probeAllLink(fn):
    try:
        lst = []
        fp = open(fn)
        for line in fp.readlines():
            l = probeLink(line)
            lst.extend(l)
    except IOError:
        print >> sys.stderr, "cannot open", fn
    return lst


def dfs(origin):
    lst = [(origin, origin, 0)]
    while 1:
        try:
            link, name, level = lst.pop(0)
        except IndexError:
            break
        prefix = " " * 4 * level
        link, name = link.encode('utf8'), name.encode('utf8')
        if sys.stdout.isatty():
            print "{}{}".format(prefix, name)
        else:
            if link == name:
                print "{}[[{}]]".format(prefix, name)
            else:
                print "{}[[{}|{}]]".format(prefix, link, name)
        ret = probeAllLink(link + '.wiki')
        level += 1
        levelret = [(node[0], node[1], level) for node in ret]
        levelret.extend(lst)
        lst = levelret

if __name__ == "__main__":
    dfs('index')
