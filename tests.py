
"""Tests and examples for SYLLABUS"""

import time
from syllabus import Task


def expensive_task(arg, task=Task()):
    """This task takes 0.25s to execute."""

    # Start timing
    task.start()

    # Print message (sends message to accounting thread)
    task.print('Child Task Process {n}'.format(n=arg))

    # Do things
    # very complicated phd-level math
    time.sleep(0.25)
    assert(1 + 1 == 2)

    # Example error reporting
    if arg % 3 == 0:
        task.error('Example error: x is a multiple of 3')

    # Example entry
    task.print('This is a long entry ' + str(arg))

    # Task done - stops timer
    task.done(desc='finished task')

    return arg


def expensive_proctask(x):
    """Wrapper of expensive_task for procpool"""

    arg, task = x
    return expensive_task(arg, task=task)


if __name__ == "__main__":

    from print import argparse

    # Initialize task; note the .start() called at the end
    main = Task("Main Task", desc='the main task', mp=False).start()

    # Single-threaded
    st1 = main.subtask("Task #1", desc='first subtask')
    expensive_task(5, task=st1)
    st2 = main.subtask("Task #1", desc='first subtask')
    expensive_task(10, task=st2)

    # Multithreading
    main.pool(expensive_task, [i for i in range(10)], process=False)

    main.done(desc="Finished!", join=True)

    if argparse.is_flag('t'):
        print("\nTask Trace:")
        print("-----------")
        print(main.json(pretty=True))
        print("\n")

    # Multiprocessing - must have mp=True enabled to use multiprocessing
    main2 = Task("MP-enabled Main Task", desc='mp=True', mp=True).start()
    main2.pool(expensive_proctask, [i for i in range(10)], process=True)
    main2.done(desc="Finished!", join=True)

    if argparse.is_flag('t'):
        print("\nTask Trace:")
        print("-----------")
        print(main2.json(pretty=True))
        print("\n")
