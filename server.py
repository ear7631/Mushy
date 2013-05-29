import sys
import traceback
import socket
import commandparser
import threading
import entity
import session
import persist

from colorer import colorfy


class LoginProxy(threading.Thread):

    def __init__(self, socket, instance):
        threading.Thread.__init__(self)
        self.socket = socket
        self.running = False
        self.instance = instance

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
        for user in self.instance.connections:
            if not isinstance(user, entity.Entity):
                continue
            if username == user.name and user.proxy.running:
                user.proxy.kill()
                self.instance.connections.remove(user)
                return
        return

    def checkIfOnline(self, username):
        for user in self.instance.connections:
            if not isinstance(user, entity.Entity):
                continue
            if username == user.name and user.proxy.running:
                return True
        return False

    def run(self):
        try:
            player = None
            self.running = True
            reconnected = False
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

            # see if it is a new user or not
            already_exists = persist.profileExists(username)

            # Grab the password
            password = ""

            # player already has a profile
            if already_exists:
                tries = 1
                self.socket.send("Enter in your password:\n")
                validated = False
                while tries < 3 and not validated:
                    password = self.socket.recv(4096).strip()
                    self.socket.send("\n")
                    validated = persist.validate(username, password)
                    if not validated:
                        self.socket.send("Incorrect, try again:\n")
                        tries += 1
                if not validated:
                    self.socket.send("Tried too many times. Disconnected.\n")
                    self.kill()
                    return

                # sanity check to make sure the player is not already connected
                if self.checkIfOnline(username):
                    choice = ''
                    while not choice in ('y', 'n'):
                        self.socket.send("Another instance of you is already connected. Kick it and take its place? (y/n) ")
                        choice = self.socket.recv(4096).strip()
                        self.socket.send("\n")

                        if choice.lower() == 'y':
                            reconnected = True
                            self.killClone(username)
                        elif choice.lower() == 'n':
                            self.kill()
                            self.socket.send("Disconnecting.\n")
                            return

                self.socket.send("Welcome back, " + username + ".\n")
                player = persist.loadEntity(username)

            # player does not have a profile
            else:
                self.socket.send("User " + username + " does not yet exist, creating a new user.\n")
                while len(password) < 4:
                    self.socket.send("Enter in your password:\n")
                    password = self.socket.recv(4096).strip()
                    self.socket.send("\n")

                    # length check
                    if len(password) < 4:
                        self.socket.send("Passwords must be at least 4 characters long.\n")
                        continue
                    repeat = ""
                    self.socket.send("Enter again to verify:\n")
                    repeat = self.socket.recv(4096).strip()
                    self.socket.send("\n")

                    # repeat check
                    if repeat != password:
                        self.socket.send("Password mis-match. Reconnect and try again.\n")
                        self.kill()
                        return

                # create a new entity and save it
                salt, hcode = persist.hashPassword(password)
                player = entity.Entity(name=username, hcode=hcode, salt=salt)

                self.socket.send("Are you the DM for the group (y if yes)? ")
                choice = self.socket.recv(4096).strip()
                self.socket.send("\n")
                dm = False
                if choice.lower() == 'y':
                    dm = True

                player.dm = dm

                self.socket.send("Profile created. Saving...\n")
                persist.saveEntity(player)

            # hook up the proxy stuff
            proxy = entity.ClientProxy(self.socket)
            player.hookProxy(proxy)

            # connect player to the instance
            player.instance = self.instance
            self.instance.connections.append(player)

            # start the proxy and notify everyone of the new connection
            player.proxy.start()
            player.sendMessage("")

            for e in self.instance.connections:
                if e == player:
                    if reconnected:
                        player.sendMessage(colorfy("[SERVER] You have reconnected.", "bright yellow"))
                    else:
                        player.sendMessage(colorfy("[SERVER] You have joined the session.", "bright yellow"))
                else:
                    if reconnected:
                        e.sendMessage(colorfy("[SERVER] " + player.name + " has reconnected.", "bright yellow"))
                    else:
                        e.sendMessage(colorfy("[SERVER] " + player.name + " has joined the session.", "bright yellow"))

            if not reconnected:
                player.sendMessage(colorfy("[SERVER] You may type 'help' at any time for a list of commands.", 'bright green'))
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=sys.stdout)
            self.running = False
            self.socket.close()
            print "Server: Client connection closed. Exception during login."


def main():

    listen_port = 8080
    if len(sys.argv) == 2:
        try:
            listen_port = int(sys.argv[1])
        except:
            print "Server: Issue when listening on port " + sys.argv[1] + ". Using default (8080)."

    print "Server: Initializing profiles."
    persist.initializeProfiles()

    print "Server: Setting up instance."
    connections = []
    instance = session.Instance(connections)

    print "Server: Starting command parser."
    commandparser.startDispatching()

    print "Server: Initialization Complete."
    print "Server: Setting up network communications."
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('', listen_port))
    server_socket.listen(0)
    print "Server: Listening on port " + str(listen_port) + ", press control+C to exit."

    done = False
    while not done:
        try:
            # client connects to the server
            client_socket, address = server_socket.accept()
            print "Server: Accepting connection from " + address[0] + "..."
            # spawn up a client proxy here
            proxy = LoginProxy(client_socket, instance)
            proxy.start()
        except KeyboardInterrupt:
            print ""
            print "Server: Closing server socket and dispatcher..."
            server_socket.close()
            commandparser.stopDispatching()
            print "Server: Closing client connections..."
            for connection in instance.connections:
                connection.proxy.kill()
            done = True
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=sys.stdout)
    print "Server: Bye!"


if __name__ == '__main__':
    main()
