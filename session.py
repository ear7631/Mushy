import stage
import entity
import turnqueue


class Session(object):

    __slots__ = ("connections", "stage", "entity_map", "tracker")

    def __init__(self):
        self.connections = {}
        self.stage = stage.Stage()
        self.tracker = turnqueue.TurnQueue()

    def add(self, player):
        self.connections[player.name.lower()] = player

    def remove(self, player):
        key = player.name.lower()
        if key in self.connections:
            del self.connections[key]

    def getEntity(self, username):
        username = username.lower()
        if username in self.connections:
            if self.connections[username].spectator:
                return None
            return self.connections[username]
        return None

    def getAllEntities(self):
        return self.connections.values()

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
        return iter(filter(lambda e: not e.spectator, self.connections.values()))