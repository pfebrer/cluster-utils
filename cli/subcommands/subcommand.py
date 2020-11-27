from types import MethodType

class SubCommand:
    _all = dict()

    def __init__(self, function, add_arguments=None, **kwargs):

        self.name = kwargs.pop("name", function.__name__)
        self.__class__._all[self.name] = self

        self.function = function
        self.add_arguments = add_arguments

        if "help" not in kwargs:
            help = (function.__doc__ or "").partition("Parameters")[0]
            kwargs["help"] = help
        self._add_parser_kwargs = kwargs
    
    @classmethod
    def get_all(cls):
        return cls._all
    
    @classmethod
    def register_all(cls, subparsers):
        for command in cls._all.values():
            command.register(subparsers)

    def register(self, subparsers):
        """ By default, we just add the command name to the subparser"""
        subparser = subparsers.add_parser(self.name, **self._add_parser_kwargs)

        if self.add_arguments is not None:
            self.add_arguments(subparser)

    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)