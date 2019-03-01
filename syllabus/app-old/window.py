from shutil import get_terminal_size
import math
import re
from print import *


ANSI_ESCAPE = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')


def span(left, right, *args):

    slen = (
        get_terminal_size().columns -
        len(ANSI_ESCAPE.sub('', left)) -
        len(ANSI_ESCAPE.sub('', right))
    )

    return render(left + render(' ' * slen, *args) + right)


def pad(val, length):

    return str(val) + ' ' * (length - len(str(val)))


class AppWindowMixins:

    __margin_width = 6
    __log_idx = 0

    def get_sizes(self):
        return [
            math.floor((get_terminal_size().lines - 4) / 2),
            math.ceil((get_terminal_size().lines - 4) / 2),
            get_terminal_size().columns - self.margin_width
        ]

    def update(self, ch):

        if ch == 'w':
            self.__log_idx -= 1
        elif ch == 'W':
            self.__log_idx = 0
        elif ch == 's':
            self.__log_idx += 1
        elif ch == 'S':
            self.__log_idx = len(self.__log)
        elif ch == 'q':
            self.done = True

    def show_header(self):

        print(span(
            render("  Syllabus | Console App  ", BG + BLACK, BR + WHITE, BOLD),
            render("  {a}  ".format(a=__author__), BG + BLACK, BR + WHITE) +
            render("  {v}  ".format(v=__version__), BG + BLUE, BR + WHITE),
            BG + BLACK))
