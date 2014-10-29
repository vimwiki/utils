#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""dfsvw.py
Create site map for vimwiki.
Must run script under vimwiki directory.

Example:
    output readable site map to stdout
        dfsvw.py
    output vimwiki-format sitemap to file
        dfsvw.py > map.wiki

Python version: 2"""
import sys
import re

linkRE = re.compile(r'\[\[([^\\\]|#]+)(?:#[^\\\]|]+)?(?:\|([^\\\]]+))?\]\]', re.UNICODE)

def probeLink(s):
    """
    >>> probeLink('   abc')
    []
    >>> probeLink('   [[]]')
    []
    >>> probeLink('   [[abc]]   [[abc|123]]  ')
    [('abc', ''), ('abc', '123')]
    >>> a, b = probeLink(' [[中文1|中文2]]')[0]; print a, b
    中文1 中文2
    >>> probeLink(' [[abc|abc 123]]')
    [('abc', 'abc 123')]
    """
    try:
        ns = s.decode('utf8')
    except UnicodeDecodeError:
        return []
    ret = linkRE.findall(ns)
    return [(a.encode('utf8'), b.encode('utf8')) for a, b in ret]


def probeAllLink(fn):
    """extract all link in a wiki file"""
    try:
        lst = []
        fp = open(fn)
        for line in fp.readlines():
            l = probeLink(line)
            lst.extend(l)
    except IOError:
        print >> sys.stderr, "cannot open", fn
    return lst


def outputNode(link, name, level):
    """output one wiki node, level for vimwiki tree hierarchy"""
    prefix = " " * 4 * level
    if not name:
        name = link
    dct = {"prefix":prefix, "link":link, "name":name}
    if sys.stdout.isatty():
        fmt = "{prefix}{name}"
    else:
        if link == name:
            fmt = "{prefix}[[{name}]]"
        else:
            fmt = "{prefix}[[{link}|{name}]]"
    print fmt.format(**dct)


def dfs(index):
    """depth first search on vimwiki
    skip searched wiki file to avoid deadloop"""
    index = index.decode('utf8')
    lst = [(index, index, [])]
    while 1:
        try:
            link, name, hist = lst.pop(0)
        except IndexError:
            break
        if link in hist:
            print >> sys.stderr, "link {} is in a circle".format(link)
            continue
        hist = hist[:]
        outputNode(link, name, len(hist))
        hist.append(link)
        ret = probeAllLink(link + '.wiki')
        levelret = [(node[0], node[1], hist) for node in ret]
        lst = levelret + lst

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print __doc__
        sys.exit(1)
    dfs('index')
