"""Interactive App Blocks

Attributes
----------
AUTHOR : str
    Author text; shown at top right
VERSION : str
    Version text; shown at top right in blue highlight
"""

from print import *
import ansiwrap
import re
from shutil import get_terminal_size


AUTHOR = "Tianshu Huang"
VERSION = "v1.0"


def screen_len(text):
    """Length of text on screen

    Parameters
    ----------
    text : str
        Text to measure

    Returns
    -------
    int
        Length of text with non-visible characters removed
    """

    return len(re.sub(r'\x1B\[[0-?]*[ -/]*[@-~]', '', text))


def span(left, right, *args):
    """Span two blocks of text

    Parameters
    ----------
    left : str
        Left aligned text
    right : str
        Right aligned text
    *args : int, str
        List of format settings for print.render
    """

    pad = get_terminal_size().columns - screen_len(left) - screen_len(right)
    return render(left + render(' ' * pad, *args) + right)


def header():
    """Interactive app header"""

    return (span(
        render("  Syllabus | Console App  ", BG + WHITE, BLACK),
        render("  {a}  ".format(a=AUTHOR), BG + WHITE, BLACK) +
        render("  {v}  ".format(v=VERSION), BG + BLUE, BR + WHITE),
        BG + WHITE))


def footer():
    """Interactive app footer"""

    return (span(
        render('  Event Log  ', BG + WHITE, BLACK),
        render(
            "[W] Up  [S] Down  [Shift+W] Top  [Shift+S] Bottom ",
            BG + WHITE, BLACK),
        BG + WHITE))


def pad(val, length):
    """Pad text with blank spaces

    Parameters
    ----------
    val : str
        Base text
    length : int
        Width to pad to

    Returns
    -------
    str
        Formatted line
    """

    return str(val) + ' ' * (length - len(str(val)))


def wrap(text, width):
    """Wrap text

    Parameters
    ----------
    text : str
        input text
    width : int
        target width

    Returns
    -------
    str[]
        List of lines
    """

    a, b = re.search(r'^( \|  )*', text).span()
    idt = text[:b]
    text = text[b:]

    return [idt + s for s in ansiwrap.wrap(text, width - len(idt))]
