import traceback
import sys
import threading
import socket
import commandparser


class Entity(object):
    def __init__(self, proxy, name, connections):
        self.proxy = proxy
        if self.proxy != None:
            self.proxy.setEntity(self)
        self.name = name
        self.connections = connections
        self.dm = False

    def sendMessage(self, message):
        if(self.proxy != None):
            self.proxy.socket.send(message + "\n")


class ClientProxy(threading.Thread):
    def __init__(self, socket):
        threading.Thread.__init__(self)
        self.socket = socket
        self.entity = None
        self.running = False

    def setEntity(self, entity):
        self.entity = entity

    def kill(self):
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
            self.socket.close()
            self.running = False
        except:
            pass

    def run(self):
        try:
            self.running = True
            while self.running:
                data = self.socket.recv(4096).strip()
                if not data:
                    continue
                else:
                    ret = commandparser.parseLine(data, self.entity)
                    if ret == False:
                        self.socket.send("What?\n")
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=sys.stdout)
            self.running = False
            self.socket.close()
            print "Client connection closed"
