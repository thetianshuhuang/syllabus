
import time
from syllabus import Task
from print import *


def expensive_task(x):

    arg, task = x
    task.reset()
    task.set_info('Child Task Process {n}'.format(n=arg))

    # Do things
    time.sleep(0.25)

    if arg % 3 == 0:
        task.error('Example error: x is a multiple of 3')

    task.info('This is a long entry ' + str(arg))
    task.done('finished task')

    return x[1]


if __name__ == "__main__":

    putil.LOG_FILE = 'log.txt'

    main = Task("Main Task", desc='the main task')

    st1 = main.subtask("Task #1", desc='first subtask')
    expensive_task([5, st1])

    st2 = main.subtask("Task #1", desc='first subtask')
    expensive_task([10, st2])

    main.pool(expensive_task, [i for i in range(10)], cores=2)

    main.done("Finished!")
