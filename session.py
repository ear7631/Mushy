from stage import Stage


class Instance(object):

    __slots__ = ("connections", "stage", "entity_map")

    def __init__(self, connections):
        self.connections = connections
        self.stage = Stage()

    def getEntity(self, client_name):
        for connection in self.connections:
            if connection.name.lower() == client_name:
                return connection
        return None

    def broadcast(self, message):
        for connection in self.connections:
            connection.sendMessage(message)

    def broadcastExclude(self, message, ignored):
        for connection in self.connections:
            if connection == ignored:
                continue
            connection.sendMessage(message)
