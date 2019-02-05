
"""Multiprocessing-like threading interface"""

# Multithreading
from multiprocessing import cpu_count
from threading import Thread, main_thread
from queue import Queue, Empty

# AsyncJob named tuple
from collections import namedtuple
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
                f, args, kwargs, task = self.arg_queue.get_nowait()
                self.result_queue.put(f(*args, task=task, **kwargs))
            except Empty:
                not_empty = False
            except Exception as e:
                print(e)
            finally:
                if not_empty:
                    self.arg_queue.task_done()

    def stop(self):
        """Stop the worker thread"""
        self.running = False


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
        self.workers = [
            Worker(self.task_queue, self.result_queue)
            for _ in range(threads)]

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

        for worker in self.workers:
            worker.start()

        # Check for task
        if task is None:
            raise Exception("No parent task supplied.")

        # Make generator expression
        genexpr = (
            AsyncJob(
                target=target, args=[arg] + list(args), kwargs=kwargs,
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

        for worker in self.workers:
            worker.stop()

        return list(self.result_queue.queue)
