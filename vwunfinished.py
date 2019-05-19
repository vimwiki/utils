import os
import sys
import argparse
from datetime import datetime

parser = argparse.ArgumentParser(description="Count unfinished vimwiki tasks")
parser.add_argument("--count-sublists", action="store_true", help="Do you wish to count sublists?")
parser.add_argument("--section", help="Count tasks only in specified section (e.g. '== Todo =='")
parser.add_argument("--bullets", help="Bullet symbols (e.g. '*-')", type=list)

parser.add_argument("--diary-dir", default="diary", help="Use nonstandard diary directory")
parser.add_argument("--wiki-path", default="~/vimwiki", help="Use nonstandard wiki path",
                    type=lambda x: os.path.expanduser(x))
parser.add_argument("--filetype", default="wiki", choices=["wiki", "md"], help="What filetype do you use?")

input_parser = parser.add_mutually_exclusive_group(required=True)
input_parser.add_argument("--path", help="Path to a vimwiki file")
input_parser.add_argument("--date", help="Use diary file for given date (in YYYY-MM-DD format)")
input_parser.add_argument("--today", help="Use diary file for today", dest="date",
                          action="store_const", const=str(datetime.now().date()))


class UnfinishedTasksCounter(object):
    def __init__(self, text=None, section=None, bullets=None, count_sublists=True):
        self.bullets = bullets or ["-", "*"]
        self.section = section
        self._text = text
        self.count_sublists = count_sublists

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
            if self.count_sublists:
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

        raise ValueError("I have not enough information to determine a file")

    @property
    def content(self):
        with open(self.path, "r") as f:
            return f.read()


def vimwiki_unfinished_tasks():
    # API
    pass


def main():
    args = parser.parse_args()
    if not os.path.exists(args.path):
        sys.exit(11)

    provider = VimwikiFileProvider(path=args.path, date=args.date, wiki_path=args.wiki_path,
                                   diary_dir=args.diary_dir, filetype=args.filetype)
    counter = UnfinishedTasksCounter(text=provider.content, section=args.section, bullets=args.bullets,
                                     count_sublists=args.count_sublists)
    print(counter.count_unfinished_tasks())


if __name__ == "__main__":
    main()
