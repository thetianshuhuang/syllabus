from .task import Task
import threading
import os
import time
from .format import format_line
from .reporting import ordered_tree
from .app_utils import getch, header, footer, wrap
from shutil import get_terminal_size
import print as p
import re


class InteractiveTaskApp(Task):

    def __init__(self, *args, refresh_rate=20, **kwargs):

        super().__init__(*args, **kwargs)

        self.__log_idx = 0
        self.__stuck_to_bottom = False
        self.__refresh_rate = refresh_rate

        self.__app_thread = threading.Thread(target=self.__app_update)
        self.__app_thread.start()

        self.__kb_thread = threading.Thread(target=self.__kb_update)
        self.__kb_thread.start()

    def draw(self):

        height = get_terminal_size().lines - 3
        width = get_terminal_size().columns

        # Text wrap
        content = []
        for line in self.render_tree().split('\n'):
            content += wrap(line, width)

        # Compute and update index
        if self.__log_idx == -1:
            self.__log_idx = max(0, len(content) - height + 2)

        if self.__stuck_to_bottom:
            idx = max(0, len(content) - height + 2)
        else:
            idx = min(
                max(self.__log_idx, 0),
                max(len(content) - height + 2, 0))

        # Assemble contents
        body_len = len(content)
        body = '\n'.join(content[idx: idx + height])

        if body_len - idx < height:
            body += '\n' * (height - body_len + idx)

        body = header() + body + '\n' + footer()

        # Print output
        os.system('cls' if os.name == 'nt' else 'clear')
        body = re.sub('\n', '\r\n', body)
        p.print(body)

    def __app_update(self):

        while threading.main_thread().is_alive() and self.end_time is None:
            self.draw()
            time.sleep(1 / self.__refresh_rate)
        self.draw()

    def __set_log_idx(self, new, relative=True):

        if relative:
            if self.__log_idx != 0 or new >= 0:
                self.__log_idx += new
        else:
            self.__log_idx = new

    def __kb_update(self):

        while threading.main_thread().is_alive() and self.end_time is None:

            ch = getch()

            if type(ch) == bytes:
                try:
                    ch = ch.decode('utf-8')
                except Exception as e:
                    ch = None

            if ch == 'w':
                self.__stuck_to_bottom = False
                self.__set_log_idx(-1)
            elif ch == 'W':
                self.__stuck_to_bottom = False
                self.__set_log_idx(0, relative=False)
            elif ch == 's':
                self.__set_log_idx(1)
            elif ch == 'S':
                self.__stuck_to_bottom = True
                self.__set_log_idx(-1, relative=False)

    def render_tree(self):

        return '\n'.join([
            format_line(line)
            for line in ordered_tree(self.accountant.tree())])
