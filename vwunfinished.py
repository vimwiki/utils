#!/usr/bin/env python3

import os
import sys
import argparse
from datetime import datetime

parser = argparse.ArgumentParser(description="Count unfinished vimwiki tasks")
parser.add_argument("--section", help="Count tasks only in specified section (e.g. '== Todo =='")
parser.add_argument("--bullets", help="Bullet symbols (e.g. '*-')", type=list)
parser.add_argument("--ignore-sublists", action="store_true", help="Do you wish to ignore sublists?")
parser.add_argument("--indentation-level", type=int,
                    help="How many characters (spaces or tabs) are before top-level tasks")

parser.add_argument("--diary-dir", default="diary", help="Use nonstandard diary directory")
parser.add_argument("--wiki-path", default="~/vimwiki", help="Use nonstandard wiki path",
                    type=lambda x: os.path.expanduser(x))
parser.add_argument("--filetype", default="wiki", choices=["wiki", "md"], help="What filetype do you use?")

input_parser = parser.add_mutually_exclusive_group(required=True)
input_parser.add_argument("--path", help="Path to a vimwiki file")
input_parser.add_argument("--date", help="Use diary file for given date (in YYYY-MM-DD format)")
input_parser.add_argument("--today", help="Use diary file for today", dest="date",
                          action="store_const", const=str(datetime.now().date()))


def vimwiki_unfinished_tasks(path=None, date=None, section=None, bullets=None, ignore_sublists=None,
                             wiki_path=None, diary_dir=None, filetype=None, indentation_level=None):
    """
    Return a count of unfinished tasks in specified vimwiki file
    Consider this function to be an API. Its attributes and return type will remain backwards compatible.

    :param str path: Path to a vimwiki file
    :param str date: Use diary file for given date (in YYYY-MM-DD format)
    :param str section: Count tasks only in specified section (e.g. '== Daily checklist ==')
    :param list bullets: Bullet symbols, e.g. ["*", "-"]
    :param bool ignore_sublists: Do you wish to ignore sublists?
    :param str wiki_path: Use nonstandard wiki path (can contain ~ for home directory)
    :param str diary_dir: Use nonstandard diary directory
    :param str filetype: Either "wiki" or "md"
    :param int indentation_level: How many characters (spaces or tabs) are before top-level tasks

    :raise: ValueError if there is not enough information to determine a wiki file
    :raise: IOError if wiki file doesn't exist

    :return: int
    """
    provider = VimwikiFileProvider(path=path, date=date, wiki_path=wiki_path,
                                   diary_dir=diary_dir, filetype=filetype)
    counter = UnfinishedTasksCounter(text=provider.content, section=section, bullets=bullets,
                                     ignore_sublists=ignore_sublists, indentation_level=indentation_level)
    return counter.count_unfinished_tasks()


class UnfinishedTasksCounter(object):
    def __init__(self, text=None, section=None, bullets=None, ignore_sublists=False, indentation_level=0):
        self.bullets = bullets or ["-", "*"]
        self.section = section
        self._text = text
        self.ignore_sublists = ignore_sublists
        self.indentation_level = indentation_level

    @property
    def text(self):
        if not self.section:
            return self._text
        level = self.section.split()[0]
        start = self._text.find(self.section)
        end = self._text.find(level, start + len(self.section))
        return self._text[start:end]

    @property
    def unfinished_bullet_str(self):
        return tuple(["{} [ ]".format(x) for x in self.bullets])

    @property
    def unfinished_tasks(self):
        tasks = []
        for line in self.text.split("\n"):
            line = line[self.indentation_level:]
            if not self.ignore_sublists:
                line = line.strip()
            if line.startswith(self.unfinished_bullet_str):
                tasks.append(line)
        return tasks

    def count_unfinished_tasks(self):
        return len(self.unfinished_tasks)


class VimwikiFileProvider(object):
    def __init__(self, path=None, date=None, wiki_path="~/vimwiki", diary_dir="diary", filetype="wiki"):
        self._path = path
        self.date = date
        self.wiki_path = wiki_path
        self.diary_dir = diary_dir
        self.filetype = filetype

    @property
    def path(self):
        if self._path:
            return os.path.expanduser(self._path)

        if self.date:
            return os.path.join(*[os.path.expanduser(self.wiki_path), self.diary_dir,
                                  ".".join([self.date, self.filetype])])

        raise ValueError("I do not have enough information to determine a file")

    @property
    def content(self):
        with open(self.path, "r") as f:
            return f.read()


def main():
    args = parser.parse_args()
    try:
        print(vimwiki_unfinished_tasks(**args.__dict__))

    except IOError as ex:
        print(ex)
        sys.exit(11)

    except ValueError as ex:
        print(ex)
        sys.exit(1)


if __name__ == "__main__":
    main()
