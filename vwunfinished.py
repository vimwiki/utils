import os
import argparse
from datetime import datetime

parser = argparse.ArgumentParser(description="Count unfinished vimwiki tasks")
parser.add_argument("--count-sublists", action="store_true", help="Do you wish to count sublists?")
parser.add_argument("--section", help="Count tasks only in specified section (e.g. '== Todo =='")
parser.add_argument("--bullets", help="Bullet symbols (e.g. '*-')", type=list)

parser.add_argument("--diary-dir", default="diary", help="Use nonstandard diary directory")
parser.add_argument("--wiki-path", default="~/vimwiki", help="Use nonstandard wiki path",
                    type=lambda x: os.path.expanduser(x))

input_parser = parser.add_mutually_exclusive_group(required=True)
input_parser.add_argument("--path", help="Path to a vimwiki file")
input_parser.add_argument("--date", help="Use diary file for given date (in YYYY-MM-DD format)")
input_parser.add_argument("--today", help="Use diary file for today", dest="date",
                          action="store_const", const=str(datetime.now().date()))


class UnfinishedTasksCounter(object):
    def __init__(self, path=None, text=None, section=None, bullets=None, count_sublists=True):
        self.path = path
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


def vimwiki_unfinished_tasks():
    # API
    pass


def main():
    args = parser.parse_args()
    counter = UnfinishedTasksCounter(path=args.path, section=args.section, bullets=args.bullets,
                                     count_sublists=args.count_sublists)
    print(counter.count_unfinished_tasks())


if __name__ == "__main__":
    main()
