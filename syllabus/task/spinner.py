
import time


def spinner(period=1):

    return '|/-\\|/-\\'[int(8 * (time.time() % period) / period)]

