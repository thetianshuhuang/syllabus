
from ..task import Task
from .getch import getch
from .window import AppWindowMixins
from queue import Empty as EmptyException


from threading import Thread, main_thread


class SyllabusApp(Task, AppWindowMixins):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__log = []
        self.__log_semaphore = False
        self.__done = False

    def accounting(self):

        try:
            update = self.reporter.get_nowait()
        except EmptyException:
            update = None

        if type(update) == dict:
            self.update(update)
        elif type(update) == str:
            self.__log.append(update)
            self.__log_semaphore = True

    def getch_init(self):

        def getch_loop():
            while main_thread().is_alive and not self.done:
                self.__kb_input = getch()
                self.__log_semaphore = True

        self.getch_thread = Thread(target=getch_loop)
        self.getch_thread.daemon = True
        self.getch_thread.start()

    def app(self):

        if self.__log_semaphore:
            self.__log_semaphore = False
            # update screen
