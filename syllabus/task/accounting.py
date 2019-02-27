"""Task Accountant (and accessories)

Usage
-----


"""

# I/O
import json
import print as p
import time
from units import size_fmt, time_fmt
from spinner import spinner

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
        "events",       # Events -- list of dicts containing time, desc, type
        "children",     # New children -- list of ids
    ])


class Accountant(threading.Thread):
    """Task Accountant

    Parameters
    ----------
    mp : bool
        Enable multiprocessing? (Use Managed Queue instead of vanilla Queue)
    root : str
        Root node ID
    """

    MSG_HEADERS = {
        "error": p.render("[ERROR]", p.BR + p.RED, p.BOLD),
        "warning": p.render("[WARNING]", p.BR + p.YELLOW, p.BOLD),
        "info": p.render("[info]", p.BR + p.BLUE, p.BOLD)
    }

    INDENT = " |  "

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
        self.task_log[update.id]["events"] += (update.events)
        self.task_log[update.id]["children"] += update.children

    def tree(self, root=None, nowait=False, previous=None):
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
            return {} if self.root is None else self.tree(self.root)
        # key not present or already visited -> return empty
        elif root not in self.task_log or root in previous:
            return {'id': root}
        # root provided -> run recursive step
        else:
            previous.append(root)
            return {
                k: v if k != 'children' else [
                    self.tree(c, previous=previous)
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

    def ordered_tree(self, tree=None, indent=0):
        """Get ordered representation of task tree

        Parameters
        ----------
        tree : dict
            Dictionary to create ordered tree from. Used by inductive step;
            should not be passed by user
        indent : int
            Current indentation level. Used by inductive step; should not be
            passed by user

        Returns
        -------
        (int, dict)[]
            [(indentation level, line contents)]
        """

        if tree is None:
            tree = self.tree()

        ordered = [(indent, {
            "id": tree["id"],
            "progress": tree.get("progress"),
            "size": tree.get("size"),
            "name": tree.get("name"),
            "desc": tree.get("desc"),
            "start_time": tree.get("start_time"),
            "end_time": tree.get("end_time")})]

        orderables = [
            c for c in tree["children"] if c.get("start_time") is not None
        ] + tree["events"]
        orderables.sort(
            key=lambda x: x["time"] if "time" in x else x["start_time"])
        ordered_single_level = orderables + [
            c for c in tree["children"] if c.get("start_time") is None]

        for event in ordered_single_level:
            if "children" in event:
                ordered += self.ordered_tree(event, indent=indent + 1)
            else:
                ordered.append((indent + 1, {
                    "body": event["body"],
                    "type": event["type"]
                }))

        return ordered

    def line_to_str(self, line):
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
        ret = self.INDENT * idt

        # Task
        if 'id' in d:

            # Task started
            if d['start_time'] is not None:

                # Task done
                if d["end_time"] is not None:
                    t, units = time_fmt(d["end_time"] - d["start_time"])
                    ret += '[x][100%][==========][{t:.2f}{u}]'.format(
                        t=t, u=units)

                # Task not done
                else:
                    t, units = time_fmt(time.time() - d["start_time"])
                    pr = d["progress"] if d["progress"] is not None else -1
                    pbar = '=' * int(pr * 10) + ' ' * (10 - int(pr * 10))
                    ret += '[{s}][{p}%][{b}][{t:.2f}{u}]'.format(
                        p='??' if pr == -1 else int(pr * 100),
                        b='N/A' if pr == -1 else pbar,
                        t=t, u=units, s=spinner(period=1))

            # Task not started
            else:
                ret += '[ ][0%]'

            # Name and description
            ret += ' {name} : {desc}'.format(name=d["name"], desc=d["desc"])

        # Message
        else:
            ret += '{h} {b}'.format(h=self.MSG_HEADERS[d["type"]], b=d["body"])

        return ret

    def __str__(self):

        return '\n'.join(
            [self.line_to_str(line) for line in self.ordered_tree()])
