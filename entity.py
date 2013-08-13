import traceback
import sys
import threading
import time
import socket
import commandparser
from mushyutils import wrap

class Entity(object):
    __slots__ = ("proxy", "name", "session", "dm", "status", "tallies",
                 "bags", "facade", "tallies_persist", "bags_persist",
                 "languages", "aliases", "hcode", "salt", "mask", "settings", "test")

    def __init__(self, name="", hcode=None, salt=None, proxy=None, session=None):
        self.proxy = proxy
        if self.proxy is not None:
            self.proxy.setEntity(self)
        self.name = name
        self.session = session
        self.dm = False
        self.mask = None
        self.status = ""
        self.tallies = {}
        self.bags = {}
        self.facade = None
        self.tallies_persist = []
        self.bags_persist = []
        self.hcode = hcode
        self.salt = salt
        self.languages = []
        self.aliases = {}
        self.settings = {
            "cols": 0,
            "saywrap": False
        }

    def sendMessage(self, message):
        if(self.proxy is not None):
            try:
                if self.settings["cols"] != 0:
                    message = wrap(message, cols=self.settings["cols"])
                self.proxy.socket.send(message + "\n")
            except:
                print "Server: Exception thrown while sending " + self.name + " a message."
                self.proxy.kill()

    def hookProxy(self, proxy):
        self.proxy = proxy
        self.proxy.setEntity(self)


class ClientProxy(threading.Thread):

    __slots__ = ("socket", "entity", "running", "bypass", "parser")

    def __init__(self, socket):
        threading.Thread.__init__(self)
        self.socket = socket
        self.entity = None
        self.running = False
        self.bypass = False
        self.parser = commandparser.CommandParser()

    def setEntity(self, entity):
        self.entity = entity

    def kill(self):
        try:
            if self.socket:
                self.socket.shutdown(socket.SHUT_RDWR)
                self.socket.close()
            self.running = False
        except:
            pass

    def run(self):
        try:
            self.running = True
            while self.running:
                if self.bypass:
                    time.sleep(0)
                else:
                    data = self.socket.recv(4096).strip()
                    if not data:
                        continue
                    else:
                        self.parser.parseLine(data, self.entity)

        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=sys.stdout)
            self.running = False
            if self.socket:
                self.socket.close()
            print "Client connection closed"