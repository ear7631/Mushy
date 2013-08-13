import sys
import traceback
import socket
import threading

import entity
import persist
import session
import commandparser

from mushyutils import colorfy, wrap


class LoginProxy(threading.Thread):

    def __init__(self, socket, session, proxy_pool):
        threading.Thread.__init__(self)
        self.socket = socket
        self.running = False
        self.session = session
        self.proxy_pool = proxy_pool

    def setEntity(self, entity):
        self.entity = entity

    def kill(self):
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
            self.socket.close()
            self.running = False
            if self in self.proxy_pool:
                self.proxy_pool.remove(self)
        except:
            pass

    def killClone(self, username):
        if username in self.session:
            clone = self.session.getEntity(username)
            clone.proxy.kill()
            del self.session.connections[username.lower()]

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
                tries = 0
                self.socket.send("Enter in your password:\n")
                validated = False
                while tries < 3 and not validated:
                    password = self.socket.recv(4096).strip()
                    self.socket.send("\n")
                    validated = persist.validate(username, password)
                    if not validated and tries < 2:
                        self.socket.send("Incorrect, try again:\n")
                        tries += 1
                if not validated:
                    self.socket.send("Tried too many times. Disconnected.\n")
                    self.kill()
                    return

                # sanity check to make sure the player is not already connected
                if username in self.session:
                    choice = ''
                    while not choice in ('y', 'n'):
                        self.socket.send("Another instance of you is already connected. Kick it and take its place? (y/n)\n")
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

                self.socket.send("Are you the DM for the group (y if yes)?\n")
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

            # connect player to the session
            player.session = self.session
            self.session.add(player)

            # start the proxy and notify everyone of the new connection
            player.proxy.start()
            player.sendMessage("")

            if reconnected:
                self.session.broadcastExclude(colorfy("[SERVER] " + player.name + " has reconnected.", "bright yellow"), player)
                player.sendMessage(colorfy("[SERVER] You have reconnected.", "bright yellow"))
            else:
                self.session.broadcastExclude(colorfy("[SERVER] " + player.name + " has joined the session.", "bright yellow"), player)
                player.sendMessage(colorfy("[SERVER] You have joined the session.", "bright yellow"))
                player.sendMessage(colorfy("[SERVER] You may type 'help' at any time for a list of commands.", 'bright green'))
                
                # Send them the newest changes as dictaded by the banner.txt file
                try:
                    banner_file = open("banner.txt")
                    banner = banner_file.read()
                    if banner:
                        player.sendMessage(colorfy("*"*80, "bright yellow"))
                        player.sendMessage(wrap(banner))
                        player.sendMessage(colorfy("*"*80, "bright yellow"))
                        banner_file.close()
                except IOError:
                    pass
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=sys.stdout)
            self.running = False
            self.socket.close()
            print "Server: Client connection closed. Exception during login."
        finally:
            if self in self.proxy_pool:
                self.proxy_pool.remove(self)


def main():
    listen_port = 8080
    if len(sys.argv) >= 2:
        try:
            listen_port = int(sys.argv[1])
        except:
            print "Server: Issue when listening on port " + sys.argv[1] + ". Using default (8080)."

    print "Server: Initializing profiles."
    persist.initializeProfiles()

    print "Server: Setting up session."
    running_session = session.Session()

    print "Server: Creating the CommandParser"
    parser = commandparser.CommandParser()

    print "Server: Initialization Complete."
    print "Server: Setting up network communications."
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('', listen_port))
    server_socket.listen(0)
    print "Server: OK."
    print "Server: Listening on port " + str(listen_port) + ", press control+C to exit.\n"

    done = False
    proxy_pool = []
    while not done:
        try:
            # client connects to the server
            client_socket, address = server_socket.accept()
            print "Server: Accepting connection from " + address[0] + "..."
            # spawn up a client proxy here
            proxy = LoginProxy(client_socket, running_session, proxy_pool)
            proxy_pool.append(proxy)
            proxy.start()
        except KeyboardInterrupt:
            print ""
            print "Server: Closing server socket and dispatcher..."
            server_socket.close()
            parser.kill()
            print "Server: Closing client connections..."
            for connection in running_session:
                connection.proxy.kill()
            for proxy in proxy_pool:
                proxy.kill()
            done = True
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=sys.stdout)
    print "Server: Bye!"


if __name__ == '__main__':
    main()
