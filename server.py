import sys
import traceback
import socket
import commandparser
import threading
import entity


class LoginProxy(threading.Thread):

    def __init__(self, socket, connections):
        threading.Thread.__init__(self)
        self.socket = socket
        self.running = False
        self.connections = connections

    def setEntity(self, entity):
        self.entity = entity

    def kill(self):
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
            self.socket.close()
            self.running = False
        except:
            pass

    def killClone(self, username):
        for user in self.connections:
            if not isinstance(user, entity.Entity):
                continue
            if username == user.name and user.proxy.running:
                user.proxy.kill()
                self.connections.remove(user)
                return
        return

    def checkIfOnline(self, username):
        for user in self.connections:
            if not isinstance(user, entity.Entity):
                continue
            if username == user.name and user.proxy.running:
                return True
        return False

    def run(self):
        try:
            self.running = True
            username = ""
            self.socket.send("-- Welcome to Mushy --\n")
            while len(username) < 1:
                self.socket.send("What is your username?\n")
                username = self.socket.recv(4096).strip()
                self.socket.send("\n")
                # validate username
                if len(username) < 1:
                    self.socket.send("Choose a REAL name!\n")

            online = self.checkIfOnline(username)
            if online:
                done = False
                while not done:
                    self.socket.send("Another instance of you is already connected. Do you want to disconnect it? (y/n)\n")
                    choice = self.socket.recv(4096).strip()

                    if choice.lower() == 'y':
                        self.killClone(username)
                        done = True
                        online = False
                    elif choice.lower() == 'n':
                        self.kill()
                        done = True

            if not online:
                proxy = entity.ClientProxy(self.socket)
                player = entity.Entity(proxy, username, self.connections)
                self.connections.append(player)
                player.proxy.start()

        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=sys.stdout)
            self.running = False
            self.socket.close()
            print "Client connection closed"


def main():
    connections = []

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('', 8888))
    server_socket.listen(0)
    print "Server: Listening on port 8888, press control+C to exit."

    commandparser.startDispatching()
    print "Server: Done."

    done = False
    while not done:
        try:
            client_socket, address = server_socket.accept()
            print "Server: Accepting connection from " + address[0] + "..."
            # spawn up a client proxy here
            proxy = LoginProxy(client_socket, connections)
            proxy.start()
        except KeyboardInterrupt:
            print ""
            print "Server: Closing server socket and dispatcher..."
            server_socket.close()
            commandparser.stopDispatching()
            print "Server: Closing client connections..."
            for connection in connections:
                if connection.proxy.running:
                    connection.proxy.kill()
            done = True
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=sys.stdout)
    print "Server: Bye!"


if __name__ == '__main__':
    main()
