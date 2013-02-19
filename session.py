class Instance(object):

    def __init__(self, connections):
        self.connections = connections
        self.objects = {}
        self.scene_title = ""
        self.scene_body = ""

    def paintSceneTitle(self, title):
        self.scene_title = title

    def paintSceneBody(self, body):
        self.scene_body = body

    def viewScene(self):
        ret = ""
        if self.scene_title == "" and self.scene_body == "":
            ret = ""

        if self.scene_title != "" and self.scene_body != "":
            ret = ret + self.scene_title + "\n" + self.scene_body

        elif self.scene_title == "":
            ret = ret + self.scene_body

        elif self.scene_body == "":
            ret = ret + self.scene_title

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
        self.scene_title = ""
        self.scene_body = ""

    def wipeObjects(self):
        self.objects.clear()
