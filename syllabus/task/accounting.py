
# Tests
import unittest

# I/O
import json
import print as p

# Threading
import threading

# Queue
from queue import Empty as EmptyException
from queue import Queue
from multiprocessing import Manager

# Update Packet definition
import collections
UpdatePacket = collections.namedtuple(
    "UpdatePacket",
    [
        "id",           # Source ID
        "data",         # Packet data -- dictionary containing keys to update
        "events",       # Events -- list of TaskEvent objects
        "children",     # New children -- list of ids
    ])


class Accountant(threading.Thread):

    def __init__(self, mp=False, root=None):

        super().__init__(daemon=True)

        if mp:
            self.queue = Manager().Queue()
        else:
            self.queue = Queue()

        self.task_log = {}
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

    def stop(self):
        """Make stop request, and block until accountant stopped"""

        self.__stop_request = True

        # Block until stopped
        while not self.stopped:
            pass

    def accounting(self):
        """Run accounting loop; called by run"""

        try:
            update = self.queue.get_nowait()
            assert isinstance(update, UpdatePacket)
        except EmptyException:
            return

        if self.root is None:
            self.root = update.id

        if update.id not in self.task_log:
            self.task_log[update.id] = {
                "events": [],
                "children": [],
                "id": update.id
            }

        self.task_log[update.id].update(update.data)
        self.task_log[update.id]["events"] += update.events
        self.task_log[update.id]["children"] += update.children

    def tree(self, root=None, nowait=False, previous=[]):
        """Get tree representation of log
        """

        # block until all task events are cleared
        if not nowait and not self.stopped:
            while self.queue.qsize() > 0:
                pass

        # no root -> base case
        if root is None:
            if self.root is None:
                return {}
            else:
                return self.tree(self.root)
        # key not present or already visited -> return empty
        elif root not in self.task_log or root in previous:
            return {'id': root}
        # root provided -> run recursive step
        else:
            previous.append(root)
            d = {
                k: v if k != 'children' else []
                for k, v in self.task_log[root].items()
            }
            for c in self.task_log[root]['children']:
                d['children'].append(self.tree(c, previous=previous))
            return d

    def json(self, root=None, pretty=False):
        """Get a json representation of the task's metadata

        Parameters
        ----------
        root : str
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


class Tests(unittest.TestCase):

    def test_accounting(self):

        accountant = Accountant(root='test-root')
        q = accountant.queue

        q.put(UpdatePacket(
            id='test-root',
            data={'start_time': 100},
            events=['test event', 'test event 2'],
            children=['test-child-1', 'test-child-2']))

        q.put(UpdatePacket(
            id='test-child-1',
            data={'foo': ['bar', 'baz']},
            events=['child event 1', 'child event 2'],
            children=[]))

        q.put(UpdatePacket(
            id='test-child-2',
            data={'foo': ['???']},
            events=[],
            children=[]))

        self.assertEqual(accountant.tree(), {
            "id": "test-root",
            "start_time": 100,
            "events": ["test event", "test event 2"],
            "children": [
                {
                    "id": "test-child-1",
                    "foo": ["bar", "baz"],
                    "events": ["child event 1", "child event 2"],
                    "children": []
                },
                {
                    "id": "test-child-2",
                    "foo": ["???"],
                    "events": [],
                    "children": []
                }
            ]
        })

        accountant.stop()
        self.assertTrue(accountant.stopped)

    def test_circular_and_undefined(self):

        accountant = Accountant(root='root')
        q = accountant.queue

        q.put(UpdatePacket(
            id='root',
            data={'is_root': True},
            events=[],
            children=['undefined-child', 'root']))

        self.assertEqual(accountant.tree(), {
            "id": "root",
            "is_root": True,
            "events": [],
            "children": [
                {"id": "undefined-child"},
                {"id": "root"},
            ]
        })

        accountant.stop()
        self.assertTrue(accountant.stopped)
