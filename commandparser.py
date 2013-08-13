import threading
import traceback
import namedtuple
import commands
import functionmapper


CommandArgs = namedtuple.namedtuple('CommandArgs', 'name tokens full actor')


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class CommandParser(object):

    __metaclass__ = Singleton
    __slots__ = ("queue", "dispatcher", "parsing", "event")

    def __init__(self):
        print "  CommandParser: Creating and launching the Dispatcher"
        self.queue = []
        self.dispatcher = Dispatcher()
        self.dispatcher.start()

    def parseLine(self, line, entity):
        line = line.strip()
        tokens = line.split(" ")
        args = CommandArgs(name=tokens[0], tokens=tokens, full=line, actor=entity)

        # This is for persistant masking
        if (args.actor.mask is not None and 
            args.name in functionmapper.commandFunctions and 
            functionmapper.commandFunctions[args.name] in commands.MASKABLE):
            newargs = CommandArgs(name=tokens[0], tokens=tokens, full=line, actor=args.actor.mask)
            args = newargs

        # This is for input blocking
        if (args.name in functionmapper.commandFunctions and 
            functionmapper.commandFunctions[args.name] in commands.INPUT_BLOCK):
            entity.proxy.bypass = True

        self.dispatcher.enqueueCommand(args)
        self.dispatcher.notify()

    def kill(self):
        self.dispatcher.kill()


class Dispatcher(threading.Thread):

    __slots__ = ("queue", "lock", "dispatching")

    def __init__(self):
        super(Dispatcher, self).__init__()
        self.lock = threading.Event()
        self.dispatching = False
        self.queue = []

    def enqueueCommand(self, args):
        self.queue.append(args)

    def notify(self):
        self.lock.set()

    def kill(self):
        self.dispatching = False
        self.lock.set()

    def run(self):
        print "    Dispatcher: Running."
        self.dispatching = True
        # need to do this shit in a new thread
        while self.dispatching:
            # block until the flag is raised
            self.lock.wait()
            if not self.dispatching:
                break
            
            # get the next command in the queue and execute it
            args = self.queue.pop()
            args = functionmapper.shorthandHandler(args)
            command = args.name

            # handle the command if it exists
            if command in functionmapper.commandFunctions:
                try:
                    ret = functionmapper.commandFunctions[command](args)  # this calls the function
                    if not ret:
                        args.actor.sendMessage("What?")
                except:
                    print "Server: An error has occured."
                    print "-----------------------------"
                    print traceback.format_exc()
            # check to see if it's an alias
            elif command in args.actor.aliases:
                new_line = args.actor.aliases[command].strip()
                new_tokens = new_line.split(" ")
                new_args = CommandArgs(name=new_tokens[0], tokens=new_tokens, full=new_line, actor=args.actor)
                self.queue.append(new_args)
                self.lock.set()
            else:
                args.actor.sendMessage("What?")

            # if that was the last command, set the block again
            if len(self.queue) == 0:
                self.lock.clear()

        print "    Dispatcher: Done."
