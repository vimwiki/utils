class UnfinishedTasksCounter(object):
    def __init__(self, path=None, text=None, section=None, bullets=None):
        self.path = path
        self.bullets = bullets or ["-", "*"]
        self.section = section
        self._text = text

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

    def count_unfinished_tasks(self):
        count = 0
        for line in self.text.split("\n"):
            if line.startswith(self.unfinished_bullet_str):
                count += 1
        return count


def vimwiki_unfinished_tasks():
    # API
    pass


def main():
    pass


if __name__ == "__main__":
    main()
