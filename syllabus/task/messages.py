

import print as p
import time


class TaskEvent:
    def __init__(self, desc, tier=0):
        self.desc = str(desc)
        self.time = time.time()
        self.tier = tier

    def __str__(self):
        return p.render("  | " * self.tier, p.BR, p.BLACK) + self.desc


class TaskError(TaskEvent):
    def __str__(self):
        return (
            p.render("  | " * self.tier, p.BR, p.BLACK) +
            p.render("[ERROR] ", p.BR + p.RED, p.BOLD) +
            str(self.desc)
        )


class TaskWarning(TaskEvent):
    def __str__(self):
        return (
            p.render("  | " * self.tier, p.BR, p.BLACK) +
            p.render("[WARNING] ", p.BR + p.YELLOW, p.BOLD) +
            str(self.desc)
        )
