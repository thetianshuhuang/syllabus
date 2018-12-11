

from print import *
import os


class TreeMixin:


    def tree(self):

        os.system('cls' if os.name == 'nt' else 'clear')

        print(self.__pad() + self.__str__())
