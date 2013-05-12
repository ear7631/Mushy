from stage import Stage


class Instance(object):

    __slots__ = ("connections", "stage")

    def __init__(self, connections):
        self.connections = connections
        self.stage = Stage()
