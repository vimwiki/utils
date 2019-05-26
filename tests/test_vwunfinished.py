import six.moves
import datetime
import unittest
from mock import patch, Mock, mock_open

from vwunfinished import (UnfinishedTasksCounter,
                          VimwikiFileProvider,
                          vimwiki_unfinished_tasks,
                          parser,)


class TestUnfinishedTasksCounter(unittest.TestCase):

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

        counter = UnfinishedTasksCounter(text=simple_text_vimwiki_syntax, section="== Todo ==")
        assert counter.text == "== Todo ==\n\n* [ ] Finish vimwiki article"  # Or ending with \n?

    def test_sublists_counter(self):
        counter = UnfinishedTasksCounter(text=text_with_sublists, ignore_sublists=False)
        assert counter.count_unfinished_tasks() == 5

        counter = UnfinishedTasksCounter(text=text_with_sublists, ignore_sublists=True)
        assert counter.count_unfinished_tasks() == 3

    def test_toplevel_indented(self):
        counter = UnfinishedTasksCounter(text=text_with_everything_indented)
        assert counter.count_unfinished_tasks() == 5

        counter = UnfinishedTasksCounter(text=text_with_everything_indented, ignore_sublists=True)
        assert counter.count_unfinished_tasks() == 0

        counter = UnfinishedTasksCounter(text=text_with_everything_indented, ignore_sublists=True, indentation_level=2)
        assert counter.count_unfinished_tasks() == 2


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


text_with_sublists = """# Text with sublists

- [ ] Some simple task
- [ ] Major task composed of multiple actions
    - [ ] Some nested task
    - [ ] Another minor task
- [ ] Another simple task
"""


simple_text_vimwiki_syntax = """= 2019-05-18 =

== Daily checklist ==

* [ ] Take a vitamin C
* [X] Eat your daily carrot!

== Todo ==

* [ ] Finish vimwiki article
"""


text_with_everything_indented = """= TODO =

  - [ ] Some long text so this needs
    to be multi-line

  - [ ] Top-level task, that is indented
    - [ ] First nesting level
      - [ ] Second nesting level
      - [ ] Some micro action
"""


class TestVimwikiFileProvider(unittest.TestCase):

    @patch("os.path.expanduser", side_effect=lambda x: x.replace("~", "/home/mockee"))
    def test_path(self, *args):
        provider = VimwikiFileProvider(path="~/foo.md")
        assert provider.path == "/home/mockee/foo.md"

        provider = VimwikiFileProvider(date="2019-05-19", filetype="md")
        assert provider.path == "/home/mockee/vimwiki/diary/2019-05-19.md"

        provider = VimwikiFileProvider(date="2019-05-19", wiki_path="/foo/", diary_dir="bar", filetype="wiki")
        assert provider.path == "/foo/bar/2019-05-19.wiki"

    def test_path_precedence(self):
        provider = VimwikiFileProvider(path="foo.md", date="2019-05-19")
        assert provider.path == "foo.md"

    def test_unspecified_path_exception(self):
        with self.assertRaises(ValueError) as context:
            provider = VimwikiFileProvider()
            provider.path
        assert "not have enough information " in str(context.exception)

    @patch("{}.open".format(six.moves.builtins.__name__), mock_open(read_data=simple_text))
    def test_content(self):
        provider = VimwikiFileProvider(path="whatever-we-mock-it.md")
        assert "## Daily checklist" in provider.content


class TestUnfinishedTasksFunction(unittest.TestCase):

    @patch("{}.open".format(six.moves.builtins.__name__), mock_open(read_data=simple_text))
    def test_vimwiki_unfinished_tasks(self):
        assert vimwiki_unfinished_tasks(path="whatever-we-mock-it.md") == 2
        assert vimwiki_unfinished_tasks(path="whatever-we-mock-it.md", section="## Daily checklist") == 1


class TestArgparser(unittest.TestCase):

    def test_input(self):
        cmd = "--path /foo/bar/baz.md"
        args = parser.parse_args(cmd.split())
        assert args.path == "/foo/bar/baz.md"

        cmd = "--date 2019-05-19"
        args = parser.parse_args(cmd.split())
        assert args.date == "2019-05-19"

        cmd = "--today"
        args = parser.parse_args(cmd.split())
        # assert args.date == "2019-05-20"  # @FIXME

    def test_section(self):
        cmd = ["--path", "foo.md", "--section", "## Todo"]
        args = parser.parse_args(cmd)
        assert args.section == "## Todo"

        cmd = ["--path", "foo.md", "--section", "=== Daily checklist ==="]
        args = parser.parse_args(cmd)
        assert args.section == "=== Daily checklist ==="

    @patch("os.path.expanduser", side_effect=lambda x: x.replace("~", "/home/mockee"))
    def test_paths(self, *args):
        cmd = ["--date", "2019-05-19", "--wiki-path", "~/vimwiki-alternative", "--diary-dir", "diary-alt"]
        args = parser.parse_args(cmd)
        assert args.wiki_path == "/home/mockee/vimwiki-alternative"
        assert args.diary_dir == "diary-alt"

    def test_bullets(self):
        cmd = "--path foo.md --bullets=*-"
        args = parser.parse_args(cmd.split())
        assert args.bullets == ["*", "-"]

        cmd = "--path foo.md --bullets=*"
        args = parser.parse_args(cmd.split())
        assert args.bullets == ["*"]

    def test_ignore_sublists(self):
        cmd = "--path foo.md"
        args = parser.parse_args(cmd.split())
        assert not args.ignore_sublists

        cmd = "--path foo.md --ignore-sublists"
        args = parser.parse_args(cmd.split())
        assert args.ignore_sublists

    def test_indentation_level(self):
        cmd = "--path foo.md --indentation-level=2"
        args = parser.parse_args(cmd.split())
        assert args.indentation_level == 2
