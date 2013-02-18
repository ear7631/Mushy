import sys
import inspect

"""
General, universal commands are defined here.

Arguments for functions, in parameter 'args' look like this:
(name, tokens, full, actor)
name - command name
tokens - full input, tokenized
full - full input, untokenized
actor - being object who used the command
"""


def catchall(args):
    return False


def help(args):
    """
    Check these helpfiles for something.
    syntax: help <subject>
            subject - the subject or command which you want to check for help on
    """
    if len(args.tokens) < 2:
        return False

    helpFunctionName = args.tokens[1]
    functions = inspect.getmembers(sys.modules[__name__], inspect.isfunction)
    docstring = None
    for functionName, function in functions:
        if functionName == helpFunctionName:
            docstring = function.__doc__

    if docstring == None:
        args.actor.sendMessage("There is no helpfile for " + args.tokens[1] + ".")
    else:
        prelude = "help file for: " + args.tokens[1] + "\n" + ("-" * len("help file for: " + args.tokens[1]))
        args.actor.sendMessage(prelude + docstring)

    return True


def say(args):
    """
    Say something out loud, in character.
    syntax: say [-l <language>] [-t <target>] <message>
            language - specific language to speak in
            target - specific target to speak to
            someone - someone you're speaking to
            message - What you would like to say

    examples:
        say hello
        >> Eitan says, "Hello."

        say -l elven "such a snob"
        >> [in elven] Eitan says, "Such a snob."

        say -t king Hello your majesty.
        >> [to king] Eitan says, "Hello your majest."

        say -l dwarven -t Gimli Sup brosef?
        >> [in dwarven to Gimli] Eitan says, "Sup, brosef?"
    """
    if len(args.tokens) < 2:
        return False

    marking = ""
    rest = ""
    msg = ""

    if args.tokens[1] == '-l':

        if not len(args.tokens) >= 4:
            return False
        marking = marking + "[in " + args.tokens[2]

        if args.tokens[3] == '-t':
            if not len(args.tokens) >= 6:
                return False
            marking = marking + " to " + args.tokens[4]
            rest = args.full[len(args.tokens[:5]):]
            rest = args.full[len(args.tokens[0] + " " + args.tokens[1] + " " + args.tokens[2]\
                + " " + args.tokens[3] + " " + args.tokens[4] + " "):]
        else:
            rest = args.full[len(args.tokens[0] + " " + args.tokens[1] + " " + args.tokens[2] + " "):]

        marking = marking + "] "

    elif args.tokens[1] == '-t':

        if not len(args.tokens) >= 4:
            return False

        marking = marking + "[to " + args.tokens[2]
        rest = args.full[len(args.tokens[0] + " " + args.tokens[1] + " " + args.tokens[2] + " "):]
        marking = marking + "] "

    if rest == "":
        msg = args.full[len(args.tokens[0]) + 1:]
    else:
        msg = rest

    msg = msg[0].upper() + msg[1:]
    if msg[-1] not in ('.', '!', '?'):
        msg = msg + '.'

    for e in args.actor.connections:
        if e == args.actor:
            e.sendMessage(marking + 'You say, "' + msg + '"')
        else:
            e.sendMessage(marking + args.actor.name + ' says, "' + msg + '"')

    return True


def pm(args):
    """
    Give a private message to someone, out of character.
    Note: This is OOC and shouldn't be abused!
    syntax: pm <player> <message>
            player - target of the pm
            message - what you would like to say privately
    """
    return False


def whisper(args):
    """
    Whisper something, in character.
    Note: Everyone will see this whisper, but should be handled ICly.
    syntax: whisper [-t <target>] <message>
            target - denoted target of the whisper if applicable
            message - what you would like to whisper
    """
    return False


def who(args):
    """
    See who is connected to the MUSH server.
    syntax: who
    """
    msg = "Currently connected players:\n"
    for e in args.actor.connections:
        msg = msg + "    " + e.name + "\n"
    e.sendMessage(msg)
    return True


def logout(args):
    """
    Logs you out of the game.
    syntax: logout
    """
    args.actor.proxy.running = False
    args.actor.sendMessage("Leaving...")
    args.actor.connections.remove(args.actor)
    args.actor.proxy.kill()
    return True
