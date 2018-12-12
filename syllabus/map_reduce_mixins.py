
"""Map Reduce Task Methods"""

import threading
from multiprocessing import Manager, Pool
from queue import Empty as EmptyException
from functools import partial


class MapReduceMixin:
    """Map Reduce Mixin

    Attributes
    ----------
    child_reporter : Queue.Queue
        Child reporter that child processes report to
    accounting_flag : bool
        Semaphore used to manage accounting threads
    is_process : bool
        True if this is a child process
    """

    def _map_reduce_init(self, is_process=False):
        """Initialize Map Reduce"""

        self.child_reporter = Manager().Queue()
        self.accounting_flag = False
        self.is_process = is_process

    def accounting(self):
        """Run one accounting iteration"""

        try:
            update = self.child_reporter.get_nowait()
        except EmptyException:
            update = None

        if type(update) == dict:
            self.children[update["id"]].update(update)
        elif type(update) == str:
            self.print(update)

    def __accounting_thread(self):
        """Function to run in an accounting thread while a pool is running"""

        self.info("started accounting")
        # Register accounting
        self.accounting_flag = True
        # Start accounting
        while threading.main_thread().is_alive and self.accounting_flag:
            self.accounting()
        self.info("stopped accounting")

    def r_reduce(self, results, reducer, split=2, cores=None):
        """Recursively reduce a list

        Parameters
        ----------
        results : T[]
            Array of arbitrary objects
        reducer : T[] -> T
            Should combine an array of up to ``split`` objects
            into a single object
        split : int
            Number of objects that should be assigned to each process;
            defaults to 2, but reducer should accept any number of inputs,
            since there may be left over objects (mod ``split```).
        cores : int
            Number of cores to use
        """

        rtask = self.subtask('Reduce', desc='Reducing Map Results')
        target = partial(reducer, task=rtask)
        while len(results) > 1:
            args = [
                results[i:i + split] for i in range(0, len(results), split)]
            p = Pool(processes=cores)
            results = p.map(target, args)

        rtask.done('Reduced Map Results')

        return results[0]

    def pool(
            self, target, args, shared_args=None, shared_init=None,
            reducer=None, recursive=True, split=2,
            name='Child Task Process', cores=None):
        """Run a task-wrapped pool

        Parameters
        ----------
        target : [arg, task] -> result
            Function to run on each argument; shared_args should be set as
            globals by shared_init.
        args : T[]
            List of parameters (arbitrary type)
        shared_args : arbitrary type
            Shared arguments to pass to each process
        shared_init : shared_args -> void
            Set globals in order to handle shared arg inheritance
        reducer : result[], task=subtask -> result
            Combines multiple results into a single object.
        recursive : bool
            If True, the reducer is run recursively with multiple processes
            to finish in O(log(n)) time.
        split : int
            Number of results to assign to each reduce iteration.
        name : str
            Name of the child processes to create
        cores : int
            Number of processes to use
        """

        # Start accounting thread
        acc = threading.Thread(target=self.__accounting_thread)
        acc.start()

        # Quick function to create a subtask
        def make_subtask():
            return self.subtask(name=name, is_process=True, started=False)

        # Set up initializer for inheritance
        if shared_args is not None and shared_init is not None:
            p = Pool(processes=cores,
                     initializer=shared_init,
                     initargs=shared_args)
        else:
            p = Pool(processes=cores)

        # Set up genexpr for args
        genexpr = (
            [arg, self.subtask(name=name, started=False)]
            for arg in args)

        # Run pool
        results = p.map(target, genexpr)

        # Kill accounting thread
        self.accounting_flag = False

        # Reduce
        if reducer is not None:
            if recursive:
                results = self.r_reduce(
                    results, reducer, split=split, cores=cores)
            else:
                results = reducer(results)

        return results
