import unittest

# Enable importing modules from parent directory
import os
parentdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
os.sys.path.insert(0, parentdir)

from vwunfinished import UnfinishedTasksCounter


class TestVWUnfinished(unittest.TestCase):

    def test_count_unfinished_tasks(self):
        counter = UnfinishedTasksCounter(text=simple_text)
        assert counter.count_unfinished_tasks() == 2

    def test_count_unfinished_dashes(self):
        counter = UnfinishedTasksCounter(text=multiple_list_types_text, bullets=["-"])
        assert counter.count_unfinished_tasks() == 2

        counter = UnfinishedTasksCounter(text=multiple_list_types_text)
        assert counter.count_unfinished_tasks() == 3

    def test_parse_section(self):
        counter = UnfinishedTasksCounter(text=simple_text, section="## Todo")
        assert counter.text == "## Todo\n\n* [ ] Finish vimwiki article"  # Or ending with \n?


simple_text = """# 2019-05-18

## Daily checklist

* [ ] Take a vitamin C
* [X] Eat your daily carrot!

## Todo

* [ ] Finish vimwiki article
"""


multiple_list_types_text = """# Text with more list types

## List with dashes

- [ ] First dashed thing
- [ ] Second dashed thing

## List with asterisks

* [ ] And here we use asterisk
"""
