
"""Task-wrapped map-reduce implementations"""

from .threadpool import Pool as ThreadPool
from multiprocessing import Pool as ProcPool
from multiprocessing import cpu_count


class ParallelMixin:

    def pool(self, *args, process=False, **kwargs):
        """Run Map-Reduce pool

        Parameters
        ----------
        process : bool
            If True, a process pool is used; if false, a thread pool is used
        """

        if process:
            if not self.mp:
                raise Exception(
                    "Task does not have multiprocessing enabled. The parent"
                    " task must have mp=True.")
            return self.__proc_pool(*args, **kwargs)
        else:
            return self.__thread_pool(*args, **kwargs)

    def __thread_pool(
            self, target, args, shared_args=[], shared_kwargs={},
            reducer=None, recursive=True, split=2,
            name='Child Task Thread', threads=None):
        """Run a task-wrapped thread pool

        Parameters
        ----------
        target : (argument, *args, task=Task, **kwargs) -> result
            Function to run on each argument; shared_args should be set as
            globals by shared_init.
        args : T[]
            List of parameters (arbitrary type)
        shared_args : {arbitrary type}
            Shared arguments to pass to each function call
        shared_kwargs : {arbitrary type}
            Shared keyword arguments to pass to each function
        reducer : result[], task=subtask -> result
            Combines multiple results into a single object.
        recursive : bool
            If True, the reducer is run recursively with multiple processes
            to finish in O(log(n)) time.
        split : int
            Number of results to assign to each reduce iteration.
        name : str
            Name of the child processes to create
        threads : int
            Number of threads to use

        Returns
        -------
        Arbitrary type or T[]
            List of reduced results generated by the provided reducer; if
            no reducer is provided, the results are returned as a list.
        """

        self.system('Set up thread map')
        p = ThreadPool(threads=threads)
        self.system(
            'Started thread pool map with {i} processes'
            .format(i=cpu_count() if threads is None else threads))
        results = p.map(
            target, args, *shared_args,
            task=self, name=name, **shared_kwargs)
        self.system("Finished map phase.")

        # Return immediately if reducer not supplied
        if reducer is None:
            return results

        self.system('Reducing results...')
        results = reducer(results)  # todo: handle recursive

        return results

    def __proc_pool(
            self, target, args,
            shared_args=None, shared_init=None,
            reducer=None, recursive=True, split=2,
            name='Child Task Process', cores=None):
        """Run a task-wrapped process pool

        Parameters
        ----------
        target : [arg, task] -> result
            Function to run on each argument; shared_args should be set as
            globals by shared_init.
        args : T[]
            List of parameters (arbitrary type)
        shared_args : [arbitrary type]
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

        Returns
        -------
        Arbitrary type or T[]
            List of reduced results generated by the provided reducer; if
            no reducer is provided, the results are returned as a list.
        """

        if shared_args is not None and shared_init is not None:
            self.system('Set up process map with initializer')
            p = ProcPool(
                processes=cores,
                initializer=shared_init,
                initargs=shared_args)

        else:
            self.system('Set up process map with no initializer')
            p = ProcPool(processes=cores)

        # Task generator expression
        genexpr = ([arg, self.subtask(name=name)] for arg in args)

        self.system(
            'Started process pool map with {i} processes'
            .format(i=cpu_count() if cores is None else cores))
        results = p.map(target, genexpr)
        self.system('Finished map phase.')

        # Return immediately if no reducer required
        if reducer is None:
            return results

        # Create reducer subtask
        rtask = self.subtask().start(
            name="Reducer", desc="Reducing Results...")
        rtask_rd = 1

        # Proceed until only one item remains
        while len(results) > 1:
            p = ProcPool(processes=cores)
            results = p.map(
                reducer, [
                    [results[i:i + split], self]
                    for i in range(0, len(results), split)
                ])

            rtask.system('Finished round {i} of reduce'.format(i=rtask_rd))
            rtask_rd += 1

        rtask.done(desc="Reduced results")

        return results[0]
