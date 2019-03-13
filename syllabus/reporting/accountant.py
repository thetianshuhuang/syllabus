"""Task Accountant (and accessories)

Usage
-----


"""

# I/O
import json

# Threading
import threading

# Queue
from queue import Empty as EmptyException
from queue import Queue
from multiprocessing import Manager


class Accountant(threading.Thread):
    """Task Accountant

    Parameters
    ----------
    mp : bool
        Enable multiprocessing? (Use Managed Queue instead of vanilla Queue)
    root : str
        Root node ID
    """

    def __init__(self, mp=False, root=None):

        super().__init__(daemon=True)

        if mp:
            self.queue = Manager().Queue()
        else:
            self.queue = Queue()

        self.task_log = {}
        self.task_log_mutex = threading.Lock()
        self.root = root

        self.__stop_request = False
        self.stopped = False

        self.start()

    def run(self):
        """Run thread

        Runs accountant while main thread is alive and stop_request flag
        not set; sets stopped attribute to True once stopped
        """
        self.stopped = False
        while threading.main_thread().is_alive() and not self.__stop_request:
            self.accounting()
        self.stopped = True

    def stop(self, nowait=False):
        """Make stop request, and block until accountant stopped

        Parameters
        ----------
        nowait : bool
            If True, stops immediately; if false, waits for queue to
            empty first.
        """

        # Block until queue empty
        if not nowait:
            while self.queue.qsize() > 0:
                pass

        # Set flag
        self.__stop_request = True

        # Block until stopped
        while not self.stopped:
            pass

    def __add_new(self, uid):
        """Add blank task"""
        if uid not in self.task_log:
            self.task_log[uid] = {"events": [], "children": [], "id": uid}

    def accounting(self):
        """Run accounting loop; called by run"""

        try:
            update = self.queue.get_nowait()
        except EmptyException:
            return

        self.task_log_mutex.acquire(True)

        if self.root is None:
            self.root = update.id

        if update["id"] not in self.task_log:
            self.__add_new(update["id"])

        if "data" in update:
            self.task_log[update["id"]].update(update["data"])
        if "events" in update:
            self.task_log[update["id"]]["events"] += update["events"]
        if "children" in update:
            self.task_log[update["id"]]["children"] += update["children"]
            for child in update["children"]:
                self.__add_new(child)

        self.task_log_mutex.release()

    def tree(self, root=None, nowait=True, previous=None):
        """Get task tree as dict

        Parameters
        ----------
        root : str or None
            Root node ID; if None, the program root is used.
        nowait : bool
            If True, the tree is computed immediately; if False, the task queue
            is cleared first.
        previous : str[]
            Used by inductive step to prevent infinite loops on illegal
            non-tree task topologies. Should not be used by the base case.

        Returns
        -------
        dict
            Dictionary representation of task tree
        """

        # block until all task events are cleared
        if not nowait and not self.stopped:
            while self.queue.qsize() > 0:
                pass

        # Clear previous
        if previous is None:
            previous = []

        # no root -> base case
        if root is None:
            if self.root is None:
                return {}
            else:
                self.task_log_mutex.acquire()
                ret = self.tree(self.root, nowait=True)
                self.task_log_mutex.release()
                return ret
        # key not present or already visited -> return empty
        elif root not in self.task_log or root in previous:
            return {'id': root}
        # root provided -> run recursive step
        else:
            previous.append(root)
            return {
                k: v if k != 'children' else [
                    self.tree(c, previous=previous, nowait=True)
                    for c in self.task_log[root]['children']]
                for k, v in self.task_log[root].items()
            }

    def json(self, root=None, pretty=False):
        """Get task tree as json

        Parameters
        ----------
        root : str or None
            Root node ID; if None, the program root is used.
        pretty : bool
            If True, a prettified json is returned. Otherwise, a minimal json
            is created.

        Returns
        -------
        json
            Json output of metadata dict
        """

        if pretty:
            return json.dumps(self.tree(root=root), indent=4, sort_keys=True)
        else:
            return json.dumps(self.tree(root=root))

    def save(self, file, pretty=False):
        """Save tree as a json to a file.

        Parameters
        ----------
        file : str
            File to save to
        pretty : bool
            Pretty or minimal json?
        """
        with open(file, 'w') as output:
            output.write(self.json(pretty=pretty))
