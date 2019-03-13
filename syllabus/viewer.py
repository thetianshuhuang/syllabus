from .reporting import ordered_tree
from .format import format_line
import json
import re


def clear_esc(text):
    return re.sub(r'\x1B\[[0-?]*[ -/]*[@-~]', '', text)


class TaskViewer():

    def __init__(self, file):

        self.file = file
        with open(file) as f:
            self.content = json.loads(f.read())

    def __str__(self):
        return '\n'.join([
            format_line(line)
            for line in ordered_tree(self.content)])

    def print(self):
        print(self.__str__())
        return self

    def save(self, file, color=False):
        with open(file, 'w') as f:
            if color:
                f.write(self.__str__())
            else:
                f.write(clear_esc(self.__str__()))
        return self
