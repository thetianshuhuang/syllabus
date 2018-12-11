
"""Task Class"""

import time
import sys

from print import *

from .memory import size_fmt
from .task_base_mixins import TaskInfoMixin
from .map_reduce_mixins import MapReduceMixin


class Task(TaskInfoMixin, MapReduceMixin):
    """Abstract Task object

    Parameters
    ----------
    name : str
        Name of the task. Defaults to 'Task' (generic task)
    desc : str
        Task description
    tier : int
        Task depth of the current task
    reporter : Queue.Queue or None
        Reporter to use when task is completed. Sends a dict containing
        task metadata.

    Attributes
    ----------
    name : str
        Name of the task; defaults to 'Task' if none is specified
    desc : str
        Description
    tier : int
        Task depth of the current task
    size : int or None
        Size of objects registered with the Task object; use for memory
        management
    end : float or None
        End time, in seconds (epoch time) if done; else None
    children : dict
        Dictionary of child tasks, keyed by their id
    start : float
        Start time, in seconds (epoch time)
    id : str
        Unique ID
    reporter : Queue.Queue
        Reporter to use when task is completed. Sends a dict containing
        task metadata.
    child_reporter : Queue.Queue
        Child reporter that child processes report to
    accounting_flag : bool
        Semaphore used to manage accounting threads
    is_process : bool
        True if this is a process; False if this is running in the main process
    """

    def __init__(
            self, name='Task', desc='',
            tier=0, reporter=None, is_process=False):

        self._info_init(name=name, desc=desc, tier=tier)
        self._map_reduce_init(is_process=is_process)
        self.reporter = reporter

        if desc != '':
            self.print("  | " * self.tier + desc)

    def __header(self):
        return "  | " * (self.tier + 1) + "<" + self.name + "> "

    def print(self, msg):

        if not self.is_process:
            print(msg)
        else:
            self.reporter.put(msg)

    def error(self, e):
        self.print(self.__header() + render(str(e), BR + RED, BOLD))

    def info(self, msg):
        self.print(self.__header() + str(msg))

    def done(self, desc, *objects, silent=False):
        """Report completion of the task

        Parameters
        ----------
        desc : str
            Updated description
        *objects : list of arbitrary objects
            The size of the objects in 'objects' is computed and used to
            report the task's memory footprint
        silent : bool
            If True, then no messages are printed.

        Returns
        -------
        Task
            self to allow method chaining
        """

        # Compute size
        self.size = sum(sys.getsizeof(obj) for obj in objects)
        self.desc = desc

        self.end = time.time()

        # Reporter
        if self.reporter is not None:
            self.reporter.put(self.metadata())

        if not silent:
            self.print(
                "  | " * self.tier + render(self.__str__(), BR + GREEN, BOLD))

        return self

    def subtask(self, name='Child Task', desc='', is_process=False):
        """Create a subtask"""

        new_task = Task(
            name=name,
            desc=desc,
            tier=self.tier + 1,
            reporter=self.child_reporter,
            is_process=is_process)
        self.children[new_task.id] = new_task

        return new_task

    def __str__(self):
        """Get string representation.

        Returns
        -------
        str
            String representation of this task. For example,
            "[1.92s | 10.82MB] <Image Loader> Loaded image example.png"
        """

        info = ["{t:.2f}s".format(t=self.runtime())]

        status = self.status()

        if status[1] > 0:
            info.append("{p:.1f}%".format(p=status[0] / status[1] * 100))

        if self.size != 0:
            units = size_fmt(self.size)
            info.append("{s:.2f}{u}".format(s=units[0], u=units[1]))

        bracket = ' | '.join(info)

        return (
            "[{b}] <{n}> {desc}"
            .format(b=bracket, n=self.name, desc=self.desc)
        )
