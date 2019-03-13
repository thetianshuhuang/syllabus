"""Task reporting methods"""

import uuid
import time
from .accountant import Accountant


class ReporterMixin:
    """Reporting Mixin for Task Class

    Parameters
    ----------
    name : str
        Desired task name
    desc : str or None
        Task description; if None, then defaults to
        '(no description available)' when displayed
    root : bool
        True if this is the root task, and False otherwise
    reporter : Accountant object
        Reporter for task tracking
    mp : bool
        True if multiprocessing should be enabled (Manager.Queue used); False
        otherwise (normal Queue; to be used with threading)
    """

    def __init__(
            self, name='Task', desc=None, root=True, reporter=None, mp=False):

        # Display parameters
        self.name = name
        self.desc = desc
        self.root = root

        # Generated Parameters
        self.start_time = None
        self.end_time = None
        self.size = 0

        # Task tracking
        self.children = {}
        self.id = str(uuid.uuid4())

        # Logging
        self.events = []

        # Progress
        self.tasks_done = 0
        self.tasks = 0

        # Handle reporter
        self.mp = mp
        if root:
            # should not provide reporter
            assert reporter is None, "Root task should not have a reporter."
            self.accountant = Accountant(mp=mp, root=self.id)
            self.reporter = self.accountant.queue
            # Bind reporter methods
            self.metadata = self.accountant.tree
            self.json = self.accountant.json
            self.save = self.accountant.save

        else:
            # Must have reporter
            assert reporter is not None, "Non-root task must have a reporter"
            self.reporter = reporter

    #
    # -- Reporter -------------------------------------------------------------
    #

    def __pass_or_get(self, target):
        """Pass target or execute, if it is a function"""

        if hasattr(target, "__call__"):
            return target()
        else:
            return target

    def update_metadata(self, *keys):
        """Send metadata update to accounting thread

        Parameters
        ----------
        *keys : str[]
            List of keys to update
        """
        self.reporter.put({
            "id": self.id,
            "data": {
                k: self.__pass_or_get(getattr(self, k))
                for k in keys}
        })

    def send_event(self, msg, event_type="info"):
        """Send event to accounting thread

        Parameters
        ----------
        msg : str or other PyObject
            Object to send to accounting thread
        event_type : "info", "error", or "warning"
            Event type (for reporter formatting)
        """
        self.reporter.put({
            "id": self.id,
            "events": [{
                "type": event_type,
                "time": time.time(),
                "body": msg}
            ]})

    def info(self, msg):
        """Send info message"""
        self.send_event(msg, "info")

    def print(self, msg):
        """Alias for info"""
        self.send_event(msg, "info")

    def error(self, e):
        """Print error"""
        self.send_event(e, "error")

    def warn(self, e):
        """Print warning"""
        self.send_event(e, "warning")

    def system(self, e):
        """System message"""
        self.send_event(e, "system")

    def system_root(self, e):
        """Root system message"""
        self.send_event(e, "root")

    #
    # -- Runtime --------------------------------------------------------------
    #

    def runtime(self):
        """Get the current runtime

        Returns
        -------
        Current runtime, in seconds; if not started, returns 0
        """

        if self.start_time is not None:
            if self.end_time is not None:
                return self.end_time - self.start_time
            else:
                return time.time() - self.start_time
        else:
            return 0

    def status(self):
        """Get number of complete and total tasks

        Returns
        -------
        (int, int)
            [0] Number of finished tasks
            [1] Total number of tasks
        """

        done = 0
        for child in self.children.values():
            if child.end_time is not None:
                done += 1
        return(done, len(self.children))

    def progress(self):
        """Get progress as a proportion

        Returns
        -------
        float
            Between 0 and 1; 0 if no tasks
        """
        if self.tasks == 0:
            return 0
        elif self.tasks_done > self.tasks:
            return 1
        else:
            return self.tasks_done / self.tasks

    def add_task(self, n):
        """Add task to task counter

        Parameters
        ----------
        n : int
            Number of tasks to add
        """
        self.tasks += n
        self.update_metadata("tasks")

    def add_progress(self, n):
        """Add to finished tasks counter

        Parameters
        ----------
        n : int
            Number of completed tasks to add
        """
        self.tasks_done += n
        self.update_metadata("progress")
