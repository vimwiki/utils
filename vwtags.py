#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
source: https://github.com/vimwiki/utils/blob/master/vwtags.py
forked from the script by EinfachToll originally committed on 24 Jun 2014 to
https://github.com/vimwiki/utils
"""

from __future__ import print_function
import sys
import re

help_text = r"""
Extracts tags from Vimwiki files. Useful for the Tagbar plugin.

Usage:
Install Tagbar (https://github.com/preservim/tagbar/). Then, put this file
anywhere and add the following to your .vimrc:

let g:tagbar_type_vimwiki = {
                        \   'ctagstype':'vimwiki'
                        \ , 'kinds':['h:header']
                        \ , 'sro':'&&&'
                        \ , 'kind2scope':{'h':'header'}
                        \ , 'sort':0
                        \ , 'ctagsbin':'/path/to/vwtags.py'
                        \ , 'ctagsargs': 'default'
                        \ }

The value of ctagsargs must be one of 'default', 'markdown' or 'media',
whatever syntax you use. However, if you use multiple wikis with different
syntaxes, you can, as a workaround, use the value 'all' instead. Then, Tagbar
will show markdown style headers as well as default/mediawiki style headers,
but there might be erroneously shown headers.
"""


class Error(Exception):
    """Base class for exceptions."""


class ReadFileIntoBufferError(Error):
    """Exception raising for failed reading file into Buffer attempt"""


if len(sys.argv) < 3:
    print(help_text)
    exit()

syntax = sys.argv[1]
filename = sys.argv[2]
rx_default_media = r"^\s*(={1,6})([^=].*[^=])\1\s*$"
rx_markdown = r"^\s*(#{1,6})([^#].*)$"
rx_fenced_code = r"^```[^\r\n]*[a-z]*(?:\n(?!```$).*)*\n```"
rx_header = None

if syntax in ("default", "media"):
    rx_header = re.compile(rx_default_media)
elif syntax == "markdown":
    rx_header = re.compile(rx_markdown)
else:
    rx_header = re.compile(rx_default_media + "|" + rx_markdown)

try:
    with open(filename, 'r') as buffer:
        file_content = buffer.readlines()
except ReadFileIntoBufferError:
    print("Failed to open file")
    exit()


def fenced_code_sentinel(filename):
    """detect fenced code zones"""
    # fenced code toggle init
    fct = 0

    # fct gen
    for line in file_content:
        if syntax == "markdown":
            fct_d = fct

            if fct_d == fct and re.match(r"```", line):
                fct = 1 - fct_d
            if re.match(r"```", line):
                yield 1
            else:
                yield fct_d
        else:
            yield fct


fcd = fenced_code_sentinel(filename)
state = [""]*6

for lnum, line in enumerate(file_content):
    fcd_toggle = next(fcd)

    if fcd_toggle == 0:
        match_header = rx_header.match(line)

        if not match_header:
            continue

        match_lvl = match_header.group(1) or match_header.group(3)
        match_tag = match_header.group(2) or match_header.group(4)

        cur_lvl = len(match_lvl)
        cur_tag = match_tag.strip()
        cur_searchterm = "^" + match_header.group(0).rstrip("\r\n") + "$"
        cur_kind = "h"

        state[cur_lvl-1] = cur_tag
        for i in range(cur_lvl, 6):
            state[i] = ""

        scope = "&&&".join(
                [state[i] for i in range(0, cur_lvl-1) if state[i] != ""])
        if scope:
            scope = "\theader:" + scope

        print('{0}\t{1}\t/{2}/;"\t{3}\tline:{4}{5}'.format(
            cur_tag, filename, cur_searchterm, cur_kind, str(lnum+1), scope))
