from click.types import ParamType


class StringList(ParamType):
    name = 'string list'

    def __init__(self, sep=None):
        ParamType.__init__(self)
        self.sep = sep

    def convert(self, value, param, ctx):
        return value.split(self.sep)
