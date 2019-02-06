
"""Task Class"""

import sys
import time
import print as p

from .memory import size_fmt
from .reporter_mixins import ReporterMixin
from .parallel_mixins import ParallelMixin


class Task(ReporterMixin, ParallelMixin):

    def __update_name(self, name=None, desc=None):
        """Update task name and/or description

        Parameters
        ----------
        name : str or None
            New name; if None, no update is performed
        desc : str or None
            New description; if None, the description is not updated
        """
        if name is not None:
            self.name = name
        if desc is not None:
            self.desc = desc

    def start(self, name=None, desc=None, silent=False):
        """Start the Task tracker

        Parameters
        ----------
        name : str or None
            Name to set
        desc : str or None
            Description to set
        silent : bool
            If True, no status is printed out

        Returns
        -------
        self
            Allow method chaining
        """

        self.__update_name(name=name, desc=desc)
        self.start_time = time.time()

        if not silent:
            self.print(self.desc, rtier=0)

        return self

    def done(self, *objects, name=None, desc=None, silent=False, join=False):
        """Mark the current task as 'done'

        Parameters
        ----------
        *objects : list of arbitrary objects
            The size of the objects in 'objects' is computed and used to
            report the task's memory footprint
        name : str or None
            Name to set
        desc : str or None
            Description to set (perhaps you want to change the description to
            reflect the status -- 'loading images' -> 'loaded images')
        silent : bool
            If True, no status is printed out.
        join : bool
            If True, spins until the task is completely cleared.
        """

        self.size = sum(sys.getsizeof(obj) for obj in objects)

        self.__update_name(name=name, desc=desc)
        self.end_time = time.time()

        if not silent:
            self.print_raw(
                p.render("  | " * self.tier, p.BR + p.BLACK) +
                p.render(self.__str__(), p.BR + p.GREEN, p.BOLD))

        if join:
            if hasattr(self, "accounting_thread"):
                while self.accounting_thread.is_alive():
                    pass

    def subtask(self, name='Child Task', desc=None):
        """Create a subtask

        Parameters
        ----------
        name : str
            Name to set
        desc : str or None
            Description to set

        Returns
        -------
        Task
            New task, registered under this task as a subtask
        """

        new_task = Task(
            name=name,
            desc=desc,
            tier=self.tier + 1,
            reporter=self.reporter,
            root=False,
            mp=self.mp)
        self.children[new_task.id] = new_task

        return new_task

    def __str__(self):
        """Get string representation

        Returns
        -------
        str
            String representation of this task. For example,
            "[1.92s | 10.82MB] <Image Loader> Loaded image example.png"
        """

        t = self.runtime()
        if t > 0.5:
            info = ["{t:.2f}s".format(t=self.runtime())]
        elif t > 0.01:
            info = ["{t:.1f}ms".format(t=t * 1000)]
        elif t > 0.001:
            info = ["{t:.2f}ms".format(t=t * 1000)]
        else:
            info = ["{t:.3f}ms".format(t=t * 1000)]

        if self.size != 0:
            val, units = size_fmt(self.size)
            info.append("{s:.2f}{u}".format(s=val, u=units))

        return (
            "[{b}] <{n}> {desc}"
            .format(b=" | ".join(info), n=self.name, desc=self.desc)
        )
