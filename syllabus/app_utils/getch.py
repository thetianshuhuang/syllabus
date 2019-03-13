"""Get Character Input

Creates "getch" function, with different structure depending on the OS.
"""

try:
    import msvcrt
    getch = msvcrt.getch
except ImportError:
    try:
        import Carbon
        assert(hasattr(Carbon, 'Evt'))

        def getch():
            if Carbon.Evt.EventAvail(0x0008)[0] == 0:
                return ''
            else:
                msg = Carbon.Evt.GetNextEvent(0x0008)[1][2]

                if ord(msg) == 3:
                    raise KeyboardInterrupt

                return chr(msg & 0x000000FF)

    except (AssertionError, ImportError, AttributeError):

        import sys
        import tty
        import termios

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
