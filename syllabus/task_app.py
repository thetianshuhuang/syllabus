from .task import Task
import threading
import print as p
import os
import time
from .format import format_line
from .reporting import ordered_tree
from .app_utils import getch, header, footer, wrap
from shutil import get_terminal_size


__version__ = 'v1.0'
__author__ = 'Tianshu Huang'


class TaskApp(Task):

    def __init__(self, *args, refresh_rate=10, **kwargs):

        super().__init__(*args, **kwargs)

        self.__log_idx = 0
        self.__refresh_rate = refresh_rate

        self.__app_thread = threading.Thread(target=self.__app_update)
        self.__app_thread.start()

        # self.__kb_thread = threading.Thread(target=self.__kb_update)
        # self.__kb_thread.start()

    def draw(self):
        os.system('cls' if os.name == 'nt' else 'clear')

        height = get_terminal_size().lines - 3
        width = get_terminal_size().columns

        content = []
        for line in self.render_tree().split('\n'):
            content += wrap(line, width)

        idx = len(content) - height
        # idx = min(max(self.__log_idx, 0), max(len(content) - height + 1, 0))

        header()
        # p.print('\n'.join(content[idx:idx + height]))
        p.print('\n'.join(content[idx: idx + height]))
        if len(content) - idx < height:
            print('\n' * (height - len(content) + idx - 1))
        footer()

    def __app_update(self):

        while threading.main_thread().is_alive():
            self.draw()
            time.sleep(1 / self.__refresh_rate)

    def __set_log_idx(self, new, relative=True):

        if relative:
            self.__log_idx += new
        else:
            self.__log_idx = new

    def __kb_update(self):

        while threading.main_thread().is_alive():
            ch = getch()

            if ch == 'w':
                self.__set_log_idx(-1)
            elif ch == 'W':
                self.__set_log_idx(0, relative=False)
            elif ch == 's':
                self.__set_log_idx(1)
            elif ch == 'S':
                self.__set_log_idx(-1, relative=False)
            elif ch == 'q' or ch == 'Q':
                self.system("stopping ...")
                self.done()

    def render_tree(self):

        return '\n'.join([
            format_line(line)
            for line in ordered_tree(self.accountant.tree())])
