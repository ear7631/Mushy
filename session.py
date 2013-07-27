import stage
import entity
import turnqueue


class Session(object):

    __slots__ = ("connections", "stage", "entity_map", "turn_queue")

    def __init__(self):
        self.connections = {}
        self.stage = stage.Stage()
        self.turn_queue = turnqueue.TurnQueue()

    def add(self, player):
        self.connections[player.name.lower()] = player

    def remove(self, player):
        key = player.name.lower()
        if key in self.connections:
            del self.connections[key]

    def getEntity(self, username):
        username = username.lower()
        if username in self.connections:
            return self.connections[username]
        return None

    def broadcast(self, message):
        for connection in self.connections.values():
            connection.sendMessage(message)

    def broadcastExclude(self, message, ignored):
        for connection in self.connections.values():
            if connection == ignored:
                continue
            connection.sendMessage(message)

    def __contains__(self, key):
        # Can take in a name or an entity object
        if isinstance(key, str):
            key = key.lower()
        elif isinstance(key, entity.Entity):
            key = key.name.lower()
        return key in self.connections

    def __iter__(self):
        return iter(self.connections.values())