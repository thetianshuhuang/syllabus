
from queue import Empty as EmptyException
from queue import Queue
from multiprocessing import Manager


class Accountant:

    def __init__(self, mp=True):

        if mp:
            self.queue = Manager().Queue()
        else:
            self.queue = Queue()

        self.task_log = {}

    def accounting(self):

        try:
            update = self.queue.get_nowait()
        except EmptyException:
            return

        if update.id not in self.task_log:
            self.task_log[update.id] = {"events": []}

        self.task_log[update.id].update(update.data)
        self.task_log[update_id]["events"].append(update.event)
