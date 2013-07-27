import colorer


class TurnQueue(object):

    # queue is the initiative queue
    # order is the in-progress ordering
    __slots__ = ("queue", "order")

    def __init__(self):
        self.queue = []
        self.order = []

    def wipe(self):
        """Wipe everything"""
        self.queue = []
        self.order = []

    def reset(self):
        """Reset the current ordering"""
        self.order = []

    def add(self, name, initiative):
        """Add a new entry to the queue"""
        i = self._index(name.lower())
        if i != -1:
            self.queue[0] = (name, initiative)
        else:
            self.queue.append((name.lower(), initiative))
        self.queue = sorted(self.queue, key=lambda x: x[1], reverse=True)

    def remove(self, name):
        i = self._index(name.lower())
        if i == -1:
            raise AttributeError
        self.queue.pop(i)

    def promote(self, name):
        name = name.lower()
        i = self._index(name)

        if i == -1:
            raise AttributeError
        elif i == 0:
            return False

        newval = self.queue[i - 1][1] + 0.001
        self.queue[i] = (name, newval)
        self.queue = sorted(self.queue, key=lambda x: x[1], reverse=True)
        return True

    def demote(self, name):
        name = name.lower()
        i = self._index(name)

        if i == -1:
            raise AttributeError
        elif i == len(self.queue) - 1:
            return False

        newval = self.queue[i + 1][1] - 0.001
        self.queue[i] = (name, newval)
        self.queue = sorted(self.queue, key=lambda x: x[1], reverse=True)
        return True

    def commit(self):
        """Commit the current queue to the ordering"""
        self.order = []
        for entry in self.queue:
            self.order.append(entry[0])

    def tick(self):
        """Take a turn"""
        if len(self.order) < 2:
            return False
        elif len(self.order) == 1:
            return True

        temp = self.order.pop(0)
        self.order.append(temp)
        return True

    def peek(self):
        if len(self.order) == 0:
            return AttributeError
        return self.order[0]

    def _index(self, name):
        for i in range(len(self.queue)):
            entry = self.queue[i]
            if entry[0] == name:
                return i
        return -1

    def __str__(self):
        s = colorer.colorfy("    Turn Order    \n", "green")
        s += "------------------\n"
        for entry in self.queue:
            s += entry[0] 
            if entry[0] == self.peek():
                s += colorer.colorfy("  <--- Current Turn", "bred")
            s += "\n"
        return s
