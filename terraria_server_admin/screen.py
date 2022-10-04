import curses


class Screen:
    def __init__(self):
        self.stdscr = None

    def __enter__(self):
        self.stdscr = curses.initscr()
        curses.cbreak()
        self.stdscr.keypad(True)

    def __exit__(self, exc_type, exc_val, exc_tb):
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.endwin()
