import functionmapper
import threading
import time
import namedtuple

CommandArgs = namedtuple.namedtuple('CommandArgs', 'name tokens full actor')
commandsToExecute = []
dispatcher = None
parsing = True


def parseLine(line, entity):
    line = line.strip()
    tokens = line.split(" ")
    args = CommandArgs(name=tokens[0], tokens=tokens, full=line, actor=entity)

    # check to see if the command exists as a common command
    if tokens[0] in functionmapper.commandFunctions:
        queueCommand(args)


def queueCommand(args):
    """Enqueues a command into the dispatch queue.
       Args is in the following form: (name tokens full actor)"""
    commandsToExecute.append(args)


def startDispatching():
    dispatcher = threading.Thread(target=dispatchForever)
    dispatcher.start()


def stopDispatching():
    global parsing
    parsing = False


def dispatchForever():
    # need to do this shit in a new thread
    while parsing:
        # If we have no commands to execute, fuck it
        if len(commandsToExecute) == 0:
            time.sleep(0)
        else:
            # get the next command in the queue and execute it
            args = commandsToExecute.pop()
            command = args[0]

            if command in functionmapper.commandFunctions:
                ret = functionmapper.commandFunctions[command](args)  # this calls the function
                if not ret:
                    args.actor.sendMessage("What?")
            else:
                args.actor.sendMessage("What?")

    print "Dispatcher: I am dead."
