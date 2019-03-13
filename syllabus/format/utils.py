"""Terminal app utilities"""

import time
import print as p
from .units import size_fmt, time_fmt


def spinner(period=1):
    """Operate 'in progress' spinner

    Parameters
    ----------
    period : float
        Period of the spinner, in seconds

    Returns
    -------
    str
        Current spinner character
    """

    return '|/-\\|/-\\'[int(8 * (time.time() % period) / period)]


MSG_HEADERS = {
    "error": p.render("[ERROR]", p.BR + p.RED, p.BOLD),
    "warning": p.render("[WARNING]", p.BR + p.YELLOW, p.BOLD),
    "info": p.render("[info]", p.BR + p.BLUE, p.BOLD),
    "system": p.render("[system]", p.BR + p.CYAN, p.BOLD),
    "root": p.render("[system]", p.BR + p.CYAN, p.BOLD),
}

INDENT = " |  "


def format_done(d):
    """Format finished line"""
    t, units = time_fmt(d["end_time"] - d["start_time"])
    return p.render(
        '[x][100%][==========][{t:.2f}{u}]'
        .format(t=t, u=units),
        p.BR + p.GREEN, p.BOLD)


def format_in_progress(d):
    """Format in progress line"""
    pr = d["progress"] if d["progress"] is not None else 0
    t, units = time_fmt(time.time() - d["start_time"])
    return p.render(
        '[{s}][{p}%][{b}][{t:.2f}{u}]'.format(
            p=int(pr * 100),
            b='=' * int(pr * 10) + ' ' * (10 - int(pr * 10)),
            t=t,
            u=units,
            s=spinner(period=1)),
        p.BR + p.BLUE, p.BOLD)


def format_not_started(d):
    """Format not started line"""
    return p.render('[ ][0%]', p.BOLD)


def format_line(line):
    """Convert line to string

    Parameters
    ----------
    line : (int, dict)
        (indentation, task dictionary)

    Returns
    -------
    str
        Line converted to string for display
    """

    idt, d = line
    if "type" in d and d["type"] == "root":
        idt = idt - 1
    ret = INDENT * idt

    # Task
    if 'id' in d:
        if d['start_time'] is not None and d["end_time"] is not None:
            ret += format_done(d)
        elif d['start_time'] is not None:
            ret += format_in_progress(d)
        else:
            ret += format_not_started(d)

        ret += ' ' + str(d["name"])
        if d["desc"] is not None:
            ret += " : " + str(d["desc"])

    # Message
    else:
        ret += '{h} {b}'.format(h=MSG_HEADERS[d["type"]], b=d["body"])

    return ret
