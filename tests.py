
"""Tests and examples for SYLLABUS"""

import time
import print as p
from syllabus import Task, BasicTaskApp, InteractiveTaskApp


def cheap_task(arg, task=None):

    task.start()
    task.print('Cheap Task {n}'.format(n=arg))
    task.done()

    return arg


def expensive_task(arg, task=None):
    """This task takes 1s to execute."""

    # Start timing
    task.start()

    task.add_task(10)

    # Print message (sends message to accounting thread)
    task.print('Child Task Process {n}'.format(n=arg))

    # Do things
    # very complicated phd-level math
    for _ in range(10):
        time.sleep(0.1)
        task.add_progress(1)
    assert(1 + 1 == 2)

    # Example error reporting
    if arg % 3 == 0:
        task.error('Example error: x is a multiple of 3')

    # Task done - stops timer
    task.done()

    return arg


def expensive_proctask(x):
    """Wrapper of expensive_task for procpool"""

    arg, task = x
    return expensive_task(arg, task=task)


if __name__ == "__main__":

    if p.argparse.is_flag('i'):
        AppClass = InteractiveTaskApp
    else:
        AppClass = BasicTaskApp


    if p.argparse.is_flag('m'):
        # Multiprocessing - must have mp=True enabled to use multiprocessing
        main2 = AppClass(
            "MP-enabled Main Task", desc='mp=True', mp=True).start()

        main2.pool(expensive_proctask, [i for i in range(10)], process=True)
        main2.pool(
            expensive_proctask, [i for i in range(10)],
            process=True, cores=2)

        main2.done()

    elif p.argparse.is_flag('l'):

        main = AppClass("Main Task", desc=' the main task', mp=False).start()
        for i in range(1000):
            expensive_task(i, task=main.subtask("Subtask #{i}".format(i=i)))
        main.done()

    else:
        # Initialize task; note the .start() called at the end
        main = AppClass("Main Task", desc='the main task', mp=False).start()

        # Single-threaded
        st1 = main.subtask("Task #1", desc='first subtask')
        expensive_task(5, task=st1)
        st2 = main.subtask("Task #2", desc='first subtask')
        expensive_task(10, task=st2)
        cheap_task(0, task=main.subtask("Task #3"))
        cheap_task(1, task=main.subtask("Task #4"))

        # Multithreading
        main.pool(expensive_task, [i for i in range(10)], process=False)

        main.done()
