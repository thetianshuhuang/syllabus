
"""Task Info Methods"""

import time
import uuid
import json


class TaskInfoMixin:
    """Task Info Mixin

    Parameters
    ----------
    name : str
        Name of the task. Defaults to 'Task' (generic task)
    desc : str
        Task description
    tier : int
        Task depth of the current task
    started : bool
        If False, the task is not labeled as started, and is only intialized.

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
    """

    def _info_init(self, name='Task', desc=None, tier=0, started=True):

        # User parameters
        self.name = name
        self.desc = desc
        self.tier = tier

        # Default parameters
        self.size = 0
        self.end = None
        self.children = {}

        # Generated Parameters
        if started:
            self.start = time.time()
        else:
            self.start = None
        self.id = uuid.uuid4()

    def metadata(self):
        """Get metadata as a dictionary

        Returns
        -------
        dict
            Task metadata; follows child relationships recursively
        """

        return {
            'start': self.start,
            'end': self.end,
            'name': self.name,
            'desc': self.desc,
            'size': self.size,
            'children': [child.metadata() for child in self.children.values()],
            'tier': self.tier,
            'id': self.id
        }

    def update(self, metadata):
        """Update task and child tasks from a metadata dictionary

        Parameters
        ----------
        metadata : dict
            Updated information
        """

        # Update information
        self.start = metadata.get('start')
        self.end = metadata.get('end')
        self.name = metadata.get('name')
        self.desc = metadata.get('desc')
        self.size = metadata.get('size')
        self.tier = metadata.get('tier')
        self.id = metadata.get('id')

        # Recursively update children
        for uid in self.children:
            try:
                self.children[uid].update(metadata["children"][uid])
            except KeyError:
                pass

    def runtime(self):
        """Get the current runtime"""
        if self.start is not None:
            return (time.time() if self.end is None else self.end) - self.start
        else:
            return 0

    def run(self, name=None, desc=None):
        """Reset the start time

        Parameters
        ----------
        name : str
            If not None, sets task name
        desc : str
            If not None, sets task description

        Returns
        -------
        Task
            self to allow method chaining
        """

        if name is not None:
            self.name = name
        if desc is not None:
            self.desc = desc

        self.about()
        self.start = time.time()
        return self

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
            if child.end is not None:
                done += 1
        return (done, len(self.children))

    def json(self):
        """Get a json representation of the task's metadata

        Returns
        -------
        json
            Json output of metadata dict
        """

        if not hasattr(self, 'metadata'):
            raise Exception(
                "MetadataMixins must be used on a class with a 'metadata' "
                "method")

        return json.dumps(self.metadata())

    def save(self, file):
        """Save metadata as a json to a file.

        Parameters
        ----------
        file : str
            File to save to
        """

        with open(file, 'w') as output:
            output.write(self.json())
