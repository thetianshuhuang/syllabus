
"""Task Class"""

import sys
import time

from .format import size_fmt, time_fmt
from .reporting import ReporterMixin
from .parallel import ParallelMixin


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

    def start(self, name=None, desc=None):
        """Start the Task tracker

        Parameters
        ----------
        name : str or None
            Name to set
        desc : str or None
            Description to set

        Returns
        -------
        self
            Allow method chaining
        """

        self.__update_name(name=name, desc=desc)
        self.start_time = time.time()
        self.update_metadata("start_time", "name", "desc")

        return self

    def done(self, *objects, name=None, desc=None, nowait=False):
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
        """

        self.size = sum(sys.getsizeof(obj) for obj in objects)

        self.__update_name(name=name, desc=desc)
        self.end_time = time.time()
        self.update_metadata("size", "end_time", "name", "desc")

        if self.root:
            self.system_root("Main task finished.")
            self.accountant.stop(nowait)

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
            reporter=self.reporter,
            root=False,
            mp=self.mp)
        self.children[new_task.id] = new_task

        self.reporter.put({
            "id": self.id,
            "children": [new_task.id]
        })

        return new_task

    def __str__(self):
        """Get string representation

        Returns
        -------
        str
            String representation of this task. For example,
            "[1.92s | 10.82MB] <Image Loader> Loaded image example.png"
        """

        val, units = time_fmt(self.runtime())
        info = ["{t:.2f}{u}".format(t=val, u=units)]

        if self.size != 0:
            val, units = size_fmt(self.size)
            info.append("{s:.2f}{u}".format(s=val, u=units))

        return (
            "[{b}] <{n}> {desc}"
            .format(b=" | ".join(info), n=self.name, desc=self.desc)
        )
