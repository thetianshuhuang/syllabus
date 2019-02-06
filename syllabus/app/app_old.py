

import re
from print import *
import os
from shutil import get_terminal_size
import math
import time
import threading

from .getch import getch

__version__ = 'v1.0'
__author__ = 'Tianshu Huang'


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


class Syllabus:

    def __init__(self):

        self.margin_width = 6
        self.log_idx = 0

        self.log = []

    def get_sizes(self):

        log_size = math.floor((get_terminal_size().lines - 4) / 2)
        tree_size = math.ceil((get_terminal_size().lines - 4) / 2)
        width = get_terminal_size().columns - self.margin_width

        return log_size, tree_size, width

    def show_header(self):

        print(span(
            render("  Syllabus | Console App  ", BG + BLACK, BR + WHITE, BOLD),
            render("  {a}  ".format(a=__author__), BG + BLACK, BR + WHITE) +
            render("  {v}  ".format(v=__version__), BG + BLUE, BR + WHITE),
            BG + BLACK))

    def show_log(self, width, height):

        self.log_idx = min(max(self.log_idx, 0), len(self.log) - height + 1)

        idx = self.log_idx
        row = 0
        while row < height:
            if idx < len(self.log):
                s = self.log[idx]
                print(
                    render(
                        pad(' ' + str(idx), self.margin_width),
                        BG + BLUE, BR + WHITE) +
                    s[:width])
                row += 1

                while len(s) > width and row < height:
                    s = s[width:]
                    print(
                        render(
                            ' ' * self.margin_width, BG + BLUE) +
                        s[:width])
                    row += 1
                idx += 1

            else:
                print(render(' ' * self.margin_width, BG + BLUE))
                row += 1

        print(span(
            render('  Event Log  ', BG + BLACK, BR + WHITE),
            render(
                "[W] Up [S] Down [Shift+W] Top [Shift+S] Bottom ",
                BG + BLACK, BR + WHITE),
            BG + BLACK))

    def show_tree(self, height):

        for i in range(height):
            print(render(' ' * self.margin_width, BG + BLUE))

        print(span(
            render('  Event Tree  ', BG + BLACK, BR + WHITE),
            render(
                "[W] Up [S] Down [D] Show [A] Hide  ",
                BG + BLACK, BR + WHITE),
            BG + BLACK))

    def refresh(self):

        os.system('clear')
        self.show_header()
        log_size, tree_size, width = self.get_sizes()
        self.show_log(width, log_size)
        self.show_tree(tree_size)

    def set_log_idx(self, new, relative=True):

        if relative:
            self.log_idx += new
        else:
            self.log_idx = new

    def kb(self):
        ch = getch()
        if ch == 'w':
            self.set_log_idx(-1)
        elif ch == 'W':
            self.set_log_idx(0, relative=False)
        elif ch == 's':
            self.set_log_idx(1)
        elif ch == 'S':
            self.set_log_idx(len(self.log), relative=False)
        elif ch == 'q' or ch == 'Q':
            self.running = False

    def loop(self):
        self.running = True
        while self.running:
            self.refresh()
            self.kb()
