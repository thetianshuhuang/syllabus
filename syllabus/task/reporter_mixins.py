
"""Task reporting methods"""

# Parameter generation
import uuid
import time

# Thread management
from threading import main_thread, Thread
from queue import Empty as EmptyException
from queue import Queue
from multiprocessing import Manager

# I/O
import print as p
import json

# Log Entry namedtuple
from collections import namedtuple
LogEntry = namedtuple('LogEntry', ['time', 'log'])


class ReporterMixin:
    """Reporting Mixin for Task Class

    Parameters
    ----------
    name : str
        Desired task name
    desc : str or None
        Task description; if None, then defaults to
        '(no description available)' when displayed
    tier : int
        Tier hierarchy of this task
    root : bool
        True if this is the root task, and False otherwise
    mp : bool
        True if multiprocessing should be enabled (Manager.Queue used); False
        otherwise (normal Queue; to be used with threading)

    Attributes
    ----------
    name, desc, tier : str, str/None, int
        Set by initializer (see above)
    start_time : float
        Start time, in seconds (epoch time); if not started, None
    end_time : float
        End time, in seconds (epoch time); if not done, None
    size : int
        Size of registered objects, in bytes
    children : dict
        Dictionary of all created subtasks
    id : str
        Unique ID for this task
    reporter : Queue
        Reporting queue
    log : list
        List of LogEntry namedtuples
    mp : bool
        Multiprocessing enabled?
    errors : str[]
        List of errors
    warnings : str[]
        List of warnings
    """

    def __init__(
            self, name='Task', desc=None, tier=0,
            root=True, reporter=None, mp=False):

        # Display parameters
        self.name = name
        self.desc = desc
        self.tier = tier
        self.root = root

        # Generated parameters
        self.start_time = None
        self.end_time = None
        self.size = 0
        self.errors = []
        self.warnings = []
        self.children = {}
        self.id = str(uuid.uuid4())

        # Handle reporter
        self.mp = mp
        if root:
            # should not provide reporter
            if reporter is not None:
                raise Exception("Root Task should not have a reporter.")
            self.accounting_init()
        else:
            # Must have reporter
            if reporter is None:
                raise Exception("Non-root task must have a reporter.")
            self.reporter = reporter

    #
    # -- Reporting ------------------------------------------------------------
    #

    def acc_join(self):
        """Spin-lock to wait for reporter print queue to empty"""

        time.sleep(0.1)
        while not self.reporter.empty():
            pass

    def accounting_init(self):
        """Initialize accounting thread"""

        if self.mp:
            self.reporter = Manager().Queue()
        else:
            self.reporter = Queue()

        def accounting_loop():
            # Main thread must be alive
            # Task must either still be running, or items left in the queue
            while (
                    main_thread().is_alive and (
                        self.end_time is None or
                        self.reporter.qsize() > 0
                    )):
                self.accounting()

        self.accounting_thread = Thread(target=accounting_loop)
        self.accounting_thread.daemon = True
        self.accounting_thread.start()

    def accounting(self):
        """Run one accounting iteration"""

        # Get next update
        try:
            update = self.reporter.get_nowait()
        except EmptyException:
            update = None

        # Dict -> status update
        if type(update) == dict:
            self.update(update)
        # Str -> print
        elif type(update) == str:
            p.print(update)

    #
    # -- Console Interface ----------------------------------------------------
    #

    def __header(self, rtier=1):
        """Get process header"""

        return (
            p.render("  | " * (self.tier + rtier), p.BR + p.BLACK) +
            "<" + self.name + "> ")

    def print_raw(self, msg):
        """Print message directly (to reporter thread)"""

        self.reporter.put(str(msg))

    def print(self, msg, rtier=1):
        """Print message (adds header)"""

        self.print_raw(self.__header(rtier=rtier) + str(msg))

    def about(self):
        """Print task information"""

        self.print(
            "(no description available)" if self.desc is None
            else self.desc)

    def error(self, e):
        """Print error"""

        self.errors.append(str(e))
        self.print(p.render("[ERROR] ", p.BR + p.RED, p.BOLD) + str(e))

    def warn(self, e):
        """Print warning"""

        self.warnings.append(str(e))
        self.print(p.render("[WARNING] ", p.YELLOW, p.BOLD) + str(e))

    #
    # -- Metadata update and export -------------------------------------------
    #

    def metadata(self):
        """Get metadata as a dictionary

        Returns
        -------
        dict
            Task metadata; follows child relationships recursively
        """

        return {
            'start_time': self.start_time,
            'end_time': self.end_time,
            'runtime': self.runtime(),
            'name': self.name,
            'desc': self.desc,
            'size': self.size,
            'children': [child.metadata() for child in self.children.values()],
            'tier': self.tier,
            'id': self.id,
            'warnings': self.warnings,
            'errors': self.errors
        }

    def update(self, metadata):
        """Recursively update task and child tasks from a metadata dictionary

        Parameters
        ----------
        metadata : dict
            Updated information
        """

        self.start_time = metadata.get('start_time')
        self.end_time = metadata.get('end_time')
        self.name = metadata.get('name')
        self.desc = metadata.get('desc')
        self.size = metadata.get('size')
        self.tier = metadata.get('tier')
        self.id = str(metadata.get('id'))
        self.warnings = metadata.get("warnings")
        self.errors = metadata.get("errors")
        # log is not updated, since only the top-level task should be tracking

        for uid in metadata["children"]:
            if uid in self.children:
                self.children[uid].update(metadata["children"][uid])

    def json(self, pretty=False):
        """Get a json representation of the task's metadata

        Parameters
        ----------
        pretty : bool
            If True, a prettified json is returned. Otherwise, a minimal json
            is created.

        Returns
        -------
        json
            Json output of metadata dict
        """

        if not hasattr(self, 'metadata'):
            raise Exception(
                "MetadataMixins must be used on a class with a 'metadata' "
                "method")

        if pretty:
            return json.dumps(self.metadata(), indent=4, sort_keys=True)
        else:
            return json.dumps(self.metadata())

    def save(self, file, pretty=False):
        """Save metadata as a json to a file.

        Parameters
        ----------
        file : str
            File to save to
        pretty : bool
            Pretty or minimal json?
        """

        with open(file, 'w') as output:
            output.write(self.json(pretty))

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
