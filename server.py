import sys
import traceback
import socket
import commandparser
import threading
import entity

from colorer import colorfy


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
            while len(username) < 1 or len(username.split()) != 1:
                self.socket.send("What will you use for a name?\n")
                username = self.socket.recv(4096).strip()
                self.socket.send("\n")
                # validate username
                if len(username) < 1:
                    self.socket.send("Choose a REAL name!\n")
                if len(username.split()) > 1:
                    self.socket.send("Only use your first name!\n")

            username = username[0].upper() + username[1:]
            online = self.checkIfOnline(username)
            if online:
                done = False
                while not done:
                    self.socket.send("Another instance of you is already connected. Do you want to take its place? (y/n)\n")
                    choice = self.socket.recv(4096).strip()

                    if choice.lower() == 'y':
                        self.killClone(username)
                        done = True
                        online = False
                    elif choice.lower() == 'n':
                        self.kill()
                        done = True

            if not online:
                self.socket.send("Are you the DM for the group? (y if yes)")
                choice = self.socket.recv(4096).strip()

                dm = False
                if choice.lower() == 'y':
                    dm = True

                proxy = entity.ClientProxy(self.socket)
                player = entity.Entity(proxy, username, self.connections)

                if dm:
                    player.dm = True

                self.connections.append(player)
                player.proxy.start()

                for e in self.connections:
                    if e == player:
                        player.sendMessage(colorfy("[SERVER] You have joined the session.", "bright yellow"))
                    else:
                        e.sendMessage(colorfy("[SERVER] " + player.name + " has joined the session.", "bright yellow"))

                player.sendMessage(colorfy("[SERVER] You may type 'help' at any time for a list of commands.", 'bright green'))
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=sys.stdout)
            self.running = False
            self.socket.close()
            print "Server: Client connection closed. Exception during login."


def main():
    connections = []

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('', 8080))
    server_socket.listen(0)
    print "Server: Listening on port 8080, press control+C to exit."

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
