class Editor(object):

    __slots__ = ("actor", "line", "lines", "socket", "text")

    def __init__(self, actor, text=""):
        self.actor = actor
        self.socket = None
        self.line = 0
        self.lines = []

    def takeFocus(self):
        self.socket = self.actor.proxy.socket
        self.actor.proxy.bypass = True

    def releaseFocus(self):
        self.socket = None
        self.actor.proxy.bypass = False

    def updateText(self):
        self.text = ""
        for line in self.lines:
            self.text = self.text + line

    def updateLines(self):
        pass

    def start(self):
        self.takeFocus()
        self.actor.sendMessage("You may enter in as many lines of text as you wish.")
        self.actor.sendMessage("Type ** on its own line to finish.")
        self.actor.sendMessage("After you are finished, your input will be echoed back to you for checking.")
        done = False

        while not done:
            data = self.socket.recv(4096)
            data = data.replace("\r\n", "\n")

            if data.strip() == "**":
                done = True
            else:
                data_lines = data.splitlines(True)
                for line in data_lines:
                    if line[-1] != "\n":
                        line = line + "\n"
                    self.lines.append(line)
                    self.line += 1

        for i in range(len(self.lines)):
            self.actor.sendMessage(str(i) + ": " + self.lines[i].strip())

        self.updateText()
        self.releaseFocus()
        self.actor.sendMessage("Leaving the Mushy editor.")
        return self.text
