import threading


class Editor(object):

    __slots__ = ("actor", "marker", "lines", "socket", "text")

    def __init__(self, actor, text=""):
        self.actor = actor
        self.marker = 0
        self.lines = []

    def updateText(self):
        self.text = ""
        for line in self.lines:
            self.text = self.text + line

    def updateLines(self):
        pass

    def launch(self, callback=None, callback_args=()):
        t = threading.Thread(target=self._start, args=(callback, callback_args))
        t.start()

    def _start(self, callback=None, callback_args=()):
        self.actor.sendMessage("You may enter in as many lines of text as you wish.")
        self.actor.sendMessage("Type ** on its own line to finish, ~help to see commands.")
        done = False
        toss = False

        while not done:
            data = self.actor.proxy.socket.recv(4096)
            data = data.replace("\r\n", "\n")
            tokens = data.strip().split(" ")

            if tokens[0] == "**":
                done = True
            elif tokens[0] == "~clear" and len(tokens) == 1:
                self.lines = []
                self.text = ""
                self.marker = 0
                self.actor.sendMessage("Document cleared.")
            elif tokens[0] == "~delete" and len(tokens) == 2:
                try:
                    i = int(tokens[1])
                    self.lines.pop(i)
                    self.marker = min(self.marker, len(self.lines) - 1)
                    self.actor.sendMessage("Deleted line " + tokens[1])
                except:
                    self.actor.sendMessage(tokens[1] + " is not a valid line number.")
            elif tokens[0] in ("~help", "~h") and len(tokens) == 1:
                self.actor.sendMessage("Possible commands:")
                self.actor.sendMessage(" ~clear         - Delete all text and start over")
                self.actor.sendMessage(" ~delete <line> - Delete a line from this document")
                self.actor.sendMessage(" ~help          - View this help text")
                self.actor.sendMessage(" ~lines         - View this document with line numbers")
                self.actor.sendMessage(" ~mark <line>   - Set the marker. Lines added will be inserted at this line.")
                self.actor.sendMessage(" ~quit          - Leave the editor, and abandon the document.")
                self.actor.sendMessage(" ~view          - View this document text")
            elif tokens[0] == "~lines" and len(tokens) == 1:
                for i in range(len(self.lines)):
                    self.actor.sendMessage(str(i) + ": " + self.lines[i].strip())
            elif tokens[0] == "~mark" and len(tokens) == 2:
                try:
                    self.marker = int(tokens[1])
                    self.actor.sendMessage("Now inserting text at line " + str(self.marker) + ".")
                except:
                    self.actor.sendMessage(tokens[1] + " is not a valid line number.")
            elif tokens[0] == "~view" and len(tokens) == 1:
                for line in self.lines:
                    self.actor.sendMessage(line.strip())
            elif tokens[0] == "~quit" and len(tokens) == 1:
                done = True
                toss = True
            else:
                data_lines = data.splitlines(True)
                for line in data_lines:
                    if line[-1] != "\n":
                        line = line + "\n"
                    self.lines.insert(self.marker, line)
                    self.actor.sendMessage(str(self.marker) + ": " + self.lines[self.marker].strip())
                    self.marker += 1

        self.updateText()
        self.actor.sendMessage("Leaving the Mushy editor.")

        self.actor.proxy.bypass = False

        if toss:
            return
        elif callback is None:
            return self.text

        return callback(callback_args, self.text)
        
        
