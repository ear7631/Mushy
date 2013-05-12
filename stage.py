class Stage(object):

    __slots__ = ("objects", "title", "body")

    def __init__(self):
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
