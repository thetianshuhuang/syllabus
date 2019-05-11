"""Get Character Input

Creates "getch" function, with different structure depending on the OS.
"""

import os


# -- Windows ------------------------------------------------------------------
if os.name == 'nt':

    import msvcrt

    def getch():
        return msvcrt.getch() if msvcrt.kbhit() else ''


# -- Linux --------------------------------------------------------------------
elif os.name == 'posix':

    import sys
    import tty
    import termios
    import os

    # Set sys.stdin.read as non-blocking
    os.set_blocking(sys.stdin.fileno(), False)

    # Create function
    def getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        if len(ch) > 0 and ord(ch) == 3:
            raise KeyboardInterrupt

        return ch


# -- Other OS -----------------------------------------------------------------
else:

    raise Exception(
        "Unsupported OS. Syllabus currently only supports keyboard input on "
        "Windows and Linux.")
