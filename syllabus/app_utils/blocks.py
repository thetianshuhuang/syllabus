from print import *
import textwrap
import re
from shutil import get_terminal_size


AUTHOR = "Tianshu Huang"
VERSION = "v1.0"


def screen_len(text):

    return len(re.sub(r'\x1B\[[0-?]*[ -/]*[@-~]', '', text))


def span(left, right, *args):

    pad = get_terminal_size().columns - screen_len(left) - screen_len(right)
    return render(left + render(' ' * pad, *args) + right)


def header():

    print(span(
        render("  Syllabus | Console App  ", BG + WHITE, BLACK),
        render("  {a}  ".format(a=AUTHOR), BG + WHITE, BLACK) +
        render("  {v}  ".format(v=VERSION), BG + BLUE, BR + WHITE),
        BG + WHITE))


def footer():

    print(span(
        render('  Event Log  ', BG + WHITE, BLACK),
        render(
            "[W] Up [S] Down [Shift+W] Top [Shift+S] Bottom ",
            BG + WHITE, BLACK),
        BG + WHITE))


def pad(val, length):

    return str(val) + ' ' * (length - len(str(val)))


def wrap(text, width):

    return [text]

    idt = len(text) - len(text.lstrip())

    return [
        ' ' * idt + row
        for row in textwrap.wrap(text.lstrip(), width - idt - 1)]
