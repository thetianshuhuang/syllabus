
"""Command Line argument parser"""

import sys


class ArgException(Exception):
    """Exception raised when invalid arguments are passed"""
    pass


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
        self.type = type
        self.name = name
        self.aliases = aliases
        self.default = default
        self.value = default
        self.desc = desc
        self.flags = flags

    def process(self, arg):
        """Process a command line argument

        Parameters
        ----------
        arg : str
            Argument to parse; single element of sys.argv[1:]

        Raises
        ------
        ArgException
            Passed value could not be converted to the desired type
        """
        if '=' in arg:
            key, value = arg.split('=')
            if key in (self.aliases + [self.name]):
                try:
                    self.value = self.type(value)
                except ValueError:
                    raise ArgException(
                        "Invalid argument type: passed value " + value +
                        " could not be converted to " + str(self.type))
        elif arg in self.flags:
            self.value = self.flags[arg]

    def get_desc(self):
        """Get description

        Returns
        -------
        str
            <description> (default=<default>)
        """

        return (
            "{desc} (default={d})"
            .format(
                desc='' if self.desc is None else self.desc,
                d='' if self.default is None else self.default)
        )


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
        """Parse sys.argv

        Returns
        -------
        Config
            self to allow for method chaining
        """

        for arg in sys.argv[1:]:
            for param in self.params:
                param.process(arg)
        return self

    def dict(self):
        """Get dictionary representation"""

        return {p.name: p.value for p in self.params}

    def get(self, key):
        """Get the value corresponding to a key

        Parameters
        ----------
        key : str
            Target parameter name

        Returns
        -------
        arbitrary type or None
            None if the key is not found
        """
        return self.dict().get(key)

    def subdict(self, *keys):
        """Get sub-dictionary with parameters for the listed values

        Parameters
        ----------
        keys : str[]
            List of desired parameters

        Returns
        -------
        dict
            Dictionary with keys and values corresponding to the provided keys
        """

        return {p.name: p.value for p in self.params if p.name in keys}

    def table(self):
        """Get table representation"""

        return [['Parameter', 'Value', 'Description']] + [
            [p.name, p.value, p.get_desc()]
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
