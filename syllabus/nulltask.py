"""Null Task Class

Has all the same function calls, but no actual functionality; use to disable
task tracking
"""

from .parallel import ParallelMixin


class NullTask(ParallelMixin):
    """Null task

    Has all methods of a normal task, but does absolutely nothing.
    Use to cleanly disable task tracking.
    """

    # Reporter mixins
    def __init__(
            self, name='Task', desc=None, root=True, reporter=None, mp=False):

        # Zeroed values
        self.name = "A Null task object"
        self.desc = "(is task tracking disabled?)"
        self.root = False
        self.start_time = None
        self.end_time = None
        self.size = 0
        self.children = {}
        self.id = ""
        self.events = []
        self.tasks_done = 0
        self.tasks = 0

        # MP flag -- is used since subtask and pool still work
        self.mp = mp

    def update_metadata(self, *keys):
        pass

    def send_event(self, msg, event_type="info"):
        pass

    def info(self, msg):
        pass

    def print(self, msg):
        pass

    def error(self, e):
        pass

    def warn(self, e):
        pass

    def system(self, e):
        pass

    def system_root(self, e):
        pass

    def runtime(self):
        return 0

    def progress(self):
        return 0

    def add_tasks(self, n):
        pass

    def add_progress(self, n):
        pass

    def set_progress(self, n):
        pass

    # Bound methods from reporter class
    def json(self, root=None, pretty=True):
        return ""

    def save(self, file, pretty=True):
        pass

    def metadata(self, root=None, nowait=True, previous=True):
        return {}

    # Main class methods
    def start(self, name=None, desc=None):
        return self

    def done(self, *objects, name=None, desc=None, nowait=False):
        pass

    def subtask(self, name='Child Task', desc=None):
        return NullTask()

    def __str__(self):
        return "Null Task object (is task tracking disabled?)"
