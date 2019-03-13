
"""Basic, non-interactive terminal app"""

import threading
import os
import time
import print as p

from .task import Task
from .format import format_line
from .reporting import ordered_tree


class BasicTaskApp(Task):
    """Basic Task App without interactive features

    Parameters
    ----------
    refresh_rate : float
        Target screen refresh rate, in Hz
    """

    def __init__(self, *args, refresh_rate=20, **kwargs):

        super().__init__(*args, **kwargs)

        self.__log_idx = 0
        self.__refresh_rate = refresh_rate

        self.__app_thread = threading.Thread(target=self.__app_update)
        self.__app_thread.start()

    def draw(self):
        """Draw screen"""

        os.system('cls' if os.name == 'nt' else 'clear')
        p.print(self.render_tree())

    def __app_update(self):
        """App update loop"""

        while threading.main_thread().is_alive() and self.end_time is None:
            self.draw()
            time.sleep(1 / self.__refresh_rate)
        self.draw()

    def render_tree(self):
        """Render task tree"""

        return '\n'.join([
            format_line(line)
            for line in ordered_tree(self.metadata())])
