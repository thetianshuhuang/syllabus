
"""Multiprocessing-like threading interface"""


from multiprocessing import cpu_count
from threading import Thread, main_thread
from queue import Queue, Empty
from collections import namedtuple
from .task import Task

AsyncJob = namedtuple('Job', ['target', 'args', 'kwargs', 'task'])


class Worker(Thread):
    """Worker thread

    Parameters
    ----------
    qrg_queue: queue.Queue
        Argument queue. Fetches items from qrg_queue until terminated; marks
        items with ```task_done```.
    result_queue: queue.Queue
        Results are put onto the result_queue.

    Attributes
    ----------
    running : bool
        Boolean flag to terminate the loop; ``run`` stops after the next
        function call if ``Worker.running`` is set to false.
    """

    def __init__(self, arg_queue, result_queue):

        super().__init__()

        self.arg_queue = arg_queue
        self.result_queue = result_queue

        self.running = True

    def run(self):
        """Run the worker thread"""

        while main_thread().is_alive() and self.running:
            not_empty = True
            try:
                f, arg, args, kwargs, task = self.arg_queue.get(timeout=1)
                self.result_queue.put(f(arg, *args, task=task, **kwargs))
            except Empty:
                not_empty = False
            except Exception as e:
                print(e)
            finally:
                if not_empty:
                    self.arg_queue.task_done()


class Pool:
    """Thread Pool object; initialize thread pool by creating workers

    Parameters
    ----------
    threads : int or None
        Number of threads to be created; if None, then cpu_count() is used
        instead.
    """

    def __init__(self, threads=None):

        if threads is None:
            threads = cpu_count()
        self.threads = threads

        self.task_queue = Queue()
        self.result_queue = Queue()

        for _ in range(threads):
            Worker(self.task_queue, self.result_queue).start()

    def map(
            self, target, arglist, *args,
            task=None, name=None, genexpr_limit=None, **kwargs):
        """Run arguments asynchronously

        Parameters
        ----------
        target : function (argument, *args, task=Task, **kwargs) -> result
            Function to run on the arguments
        arglist : list
            List of arguments to map over
        *args : list
            List of additional arguments; these arguments are passed to each
            function
        task : Task or None
            task to register subtasks under
        name : str or None
            default name of the generated task
        **kwargs : dict
            Keyword arguments to pass to each function
        """

        # Make new task if none exists
        if task is None:
            task = Task('Child Thread')

        # Make generator expression
        genexpr = (
            AsyncJob(
                target=target, args=[arg] + args, kwargs=kwargs,
                task=task.subtask(name=name))
            for arg in arglist)

        # Default genexpr_limit to number of threads; this should be
        # increased for fast consumers
        if genexpr_limit is None:
            genexpr_limit = self.threads

        # Create jobs until StopIteration is reached
        for job in genexpr:

            # Spin if queue is too large
            while (
                    main_thread().is_alive() and
                    self.task_queue.qsize() > genexpr_limit):
                pass

            # Add job
            self.task_queue.put(job)

        # Wait for all jobs to finish
        self.task_queue.join()
        return list(self.result_queue.queue)
