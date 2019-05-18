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
    pass


if __name__ == "__main__":
    main()
