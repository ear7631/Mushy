from colorer import colors as swatch


class Stage(object):

    __slots__ = ("objects", "title", "body", "brushes")

    def __init__(self):
        self.brushes = {}
        self.objects = {}
        self.title = ""
        self.body = ""

    def paintSceneTitle(self, title):
        self.title = title

    def paintSceneBody(self, body):
        self.body = body

    def viewScene(self):
        ret = ""
        if self.title == "" and self.body == "":
            ret = ""

        if self.title != "" and self.body != "":
            ret = ret + self.title + "\n" + self.body

        elif self.title == "":
            ret = ret + self.body

        elif self.body == "":
            ret = ret + self.title

        if len(self.objects) == 0:
            return ret

        ret = ret + "\nYou see a few items of interest:\n"
        for item in self.objects:
            ret = ret + "    " + item + "\n"
        return ret

    def paintObject(self, identifier, description):
        self.objects[identifier.lower()] = description

    def viewObject(self, identifier):
        if identifier.lower() in self.objects:
            return self.objects[identifier.lower()]
        return ""

    def eraseObject(self, identifier):
        if identifier.lower() in self.objects:
            del self.objects[identifier.lower()]

    def wipeScene(self):
        self.title = ""
        self.body = ""

    def wipeObjects(self):
        self.objects.clear()

    def _initBrush(self, entity):
        if not entity in self.brushes:
            self.brushes[entity] = "white"

    def setBrush(self, entity, color):
        self._initBrush(entity)
        if color in swatch:
            self.brushes[entity] = color
        else:
            self.brushes[entity] = "white"

    def resetBrush(self, entity):
        self._initBrush(entity)
        self.brushes[entity] = "white"

    def getBrush(self, entity):
        self._initBrush(entity)
        return self.brushes[entity]
