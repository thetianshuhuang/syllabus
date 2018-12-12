
"""Command Line argument parser"""

import sys


class Param:
    """Command line parameter

    Parameters
    ----------
    name : str
        Parameter name
    aliases : str[]
        List of alternative names that can be used
    flags : dict (str->arbitrary type)
        Dictionary of flags, and their corresponding values
    type : function (str->arbitrary type)
        Type conversion
    default : arbitrary type
        Default value of the parameter
    desc : str
        Parameter description
    """

    def __init__(
            self, name,
            aliases=[], flags={},
            type=str, default=None, desc=None):
        self.name = name
        self.aliases = aliases
        self.default = default
        self.value = None
        self.desc = desc

    def process(self, arg):
        """Process a command line argument

        Parameters
        ----------
        arg : str
            Argument to parse; single element of sys.argv[1:]
        """
        if '=' in arg:
            key, value = arg.split('=')
            if key in (self.aliases + [self.name]):
                self.value = self.type(value)
        elif arg in self.flags:
            self.value = self.flags[arg]


class Config:
    """Generate configurator

    Parameters
    ----------
    params : str[]
        List of parameters to use
    """

    def __init__(self, *params):
        self.params = params

    def parse(self):
        """Parse sys.argv"""

        for arg in sys.argv[1:]:
            for param in self.params:
                param.process(arg)

    def dict(self):
        """Get dictionary representation"""

        return {p.name: p.value for p in self.params}

    def __desc(self):
        """Get description"""

        return (
            "{desc} (default={d})"
            .format(
                desc='' if self.desc is None else self.desc,
                d='' if self.default is None else self.default)
        )

    def table(self):
        """Get table representation"""

        return [
            [p.name, p.value, self.__desc()]
            for p in self.params
        ]

    def print(self, padding=' ' * 4):
        """Print out parameters;
        If print.table is available, print out a table instead.

        Parameters
        ----------
        padding : str
            Padding to put to the left of the table
        """
        try:
            from print import table
            table.table(self.table(), padding=padding)
        except ImportError:
            for row in self.table():
                print(padding + str(row))
