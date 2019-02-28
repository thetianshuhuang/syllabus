from .task import Task
import threading
import print as p
import os
import time
from .units import size_fmt, time_fmt
from .utils import format_line


def ordered_tree(tree, indent=0):
    """Get ordered representation of a task tree

    Parameters
    ----------
    tree : dict
        Dictionary to create ordered tree from.
    indent : int
        Current indentation level. Used by inductive step; should not be
        passed by user

    Returns
    -------
    (int, dict)[]
        [(indentation level, line contents)]
    """

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
            ordered += ordered_tree(event, indent=indent + 1)
        else:
            ordered.append((indent + 1, {
                "body": event["body"],
                "type": event["type"]
            }))

    return ordered


class TaskApp(Task):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        t = threading.Thread(target=self.__app_update)
        t.start()

    def __app_update(self):

        print("started")

        while threading.main_thread().is_alive() and self.end_time is None:
            os.system('cls' if os.name == 'nt' else 'clear')
            p.print(self.render_tree())
            time.sleep(0.1)

    def render_tree(self):

        return '\n'.join([
            format_line(line)
            for line in ordered_tree(self.accountant.tree())])
