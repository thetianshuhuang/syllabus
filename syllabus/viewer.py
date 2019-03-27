"""Viewer for saved JSON logs"""

from .reporting import ordered_tree
from .format import format_line
import json
import re


def clear_esc(text):
    """Clear escape sequences"""
    return re.sub(r'\x1B\[[0-?]*[ -/]*[@-~]', '', text)


class TaskViewer():
    """Viewer for saved JSON logs

    Parameters
    ----------
    file : str
        File to open
    """

    def __init__(self, file):

        self.file = file
        with open(file) as f:
            self.content = json.loads(f.read())

    def __str__(self):
        """Get string representation"""
        return '\n'.join([
            format_line(line)
            for line in ordered_tree(self.content)])

    def print(self):
        """Print formatted log"""
        print(self.__str__())
        return self

    def save(self, file, color=False):
        """Save log to file

        Parameters
        ----------
        file : str
            Output file
        color : bool
            If False, ANSI escape sequences are stripped before saving.
        """
        with open(file, 'w') as f:
            if color:
                f.write(self.__str__())
            else:
                f.write(clear_esc(self.__str__()))
        return self
