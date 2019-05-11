"""Interactive Terminal App"""

# Main loop control
import threading
import time

# Output
import os
import print as p

# Output Formatting
from shutil import get_terminal_size
import re

# Dependencies
from .task import Task
from .format import format_line
from .reporting import ordered_tree
from .app_utils import getch, header, footer, wrap


class InteractiveTaskApp(Task):
    """Interactive terminal app

    Parameters
    ----------
    refresh_rate : float
        Output refresh rate, in Hz
    """

    __NOCURSOR = '  '
    __CURSOR = ' >'

    def __init__(self, *args, refresh_rate=20, **kwargs):

        super().__init__(*args, **kwargs)

        self.__log_idx = 0
        self.__cursor = 0
        self.__stuck_to_bottom = False
        self.__refresh_rate = refresh_rate

        self.__app_thread = threading.Thread(target=self.__app_update)
        self.__app_thread.start()

        self.__kb_thread = threading.Thread(target=self.__kb_update)
        self.__kb_thread.start()

    def draw(self):
        """Draw terminal app"""

        height = get_terminal_size().lines - 3
        width = get_terminal_size().columns

        # Text wrap
        content = []
        for line in self.render_tree().split('\n'):
            content += wrap(line, width)

        # Compute and update index
        max_log_idx = max(0, len(content) - height + 2)

        # Index = -1 (jump to bottom) or index greater than allowed or
        # sticky bottom enabled => set to greatest allowed
        if (
                self.__log_idx < 0 or
                self.__log_idx > max_log_idx or
                self.__stuck_to_bottom):
            self.__log_idx = max_log_idx
        # Cursor = -1 (jump to bottom) or cursor greater than allowed or
        # sticky bottom enabled => set to greatest allowed
        if (
                self.__cursor == -1 or
                self.__cursor >= len(content) or
                self.__stuck_to_bottom):
            self.__cursor = max(0, len(content) - 1)
            self.__log_idx = max_log_idx

        # Draw cursor
        content[self.__cursor] = self.__CURSOR + content[self.__cursor][2:]

        # Assemble contents
        body_len = len(content)
        body = '\n'.join(content[self.__log_idx: self.__log_idx + height])

        if body_len - self.__log_idx < height:
            body += '\n' * (height - body_len + self.__log_idx)

        body = header() + body + '\n' + footer()

        # Print output
        os.system('cls' if os.name == 'nt' else 'clear')
        body = re.sub('\n', '\r\n', body)
        p.print(body)

    def __app_update(self):
        """App update loop"""

        while threading.main_thread().is_alive() and self.end_time is None:
            self.draw()
            time.sleep(1 / self.__refresh_rate)
        self.draw()

    def __set_log_idx(self, new, relative=True):
        """Set current index

        Parameters
        ----------
        new : int
            New index
        relative : bool
            if True, new is added to the current; if False, the index is
            overwritten
        """

        # Index
        if relative:
            if (
                    (self.__log_idx != 0 or new >= 0) and
                    self.__cursor - self.__log_idx == 2):
                self.__log_idx += new
            if self.__cursor != 0 or new >= 0:
                self.__cursor += new
        else:
            self.__log_idx = new
            self.__cursor = new

    def __kb_update(self):
        """Keyboard update loop"""

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
            elif ch == ' ':
                pass

            time.sleep(0.05)

    def render_tree(self):
        """Render task tree

        Returns
        -------
        str
            Rendered tree
        """

        return '\n'.join([
            self.__NOCURSOR + format_line(line)
            for idx, line in enumerate(ordered_tree(self.metadata()))])
