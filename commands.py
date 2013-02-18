import sys
import inspect
import random
from colorer import colorfy

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
        prelude = colorfy(prelude, 'green')
        args.actor.sendMessage(prelude + docstring)

    return True


def say(args):
    """
    Say something out loud, in character. Unless otherwise specified, things are said in common.
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
        >> [to king] Eitan says, "Hello your majesty."

        say -l dwarven -t Gimli Sup brosef?
        >> [in dwarven to Gimli] Eitan says, "Sup, brosef?"


    Alternatively, as a shorthand, you may start the say command with the "'" token (no space).

    example:
        'Hello, everyone!
        >>Eitan says, "Hello, everyone!"
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
            rest = args.full[len(args.tokens[0] + " " + args.tokens[1] + " " + args.tokens[2]
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

    marking = colorfy(marking, 'yellow')
    for e in args.actor.connections:
        if e == args.actor:
            e.sendMessage(marking + colorfy('You say, "' + msg + '"', "white"))
        else:
            e.sendMessage(marking + colorfy(args.actor.name + ' says, "' + msg + '"', "white"))

    return True


def pm(args):
    """
    Give a private message to someone, out of character. Other people cannot see these messages.
    Note: This is OOC and shouldn't be abused!
    syntax: pm <player> <message>
            player - target of the pm
            message - what you would like to say privately
    """
    if not len(args.tokens) >= 3:
        return False

    for e in args.actor.connections:
        if e.name.lower() == args.tokens[1].lower():
            e.sendMessage(colorfy("[" + args.actor.name + ">>] " +
                          args.full[len(args.tokens[0] + " " + args.tokens[1] + " "):], 'purple'))
            args.actor.sendMessage(colorfy("[>>" + e.name + "] " +
                                   args.full[len(args.tokens[0] + " " + args.tokens[1] + " "):], 'purple'))
    return True


def whisper(args):
    """
    Say something out loud, in character.
    syntax: whisper [-l <language>] [-t <target>] <message>
            language - specific language to speak in
            target - specific target to speak to
            someone - someone you're speaking to
            message - What you would like to say

    examples:
        whisper hello
        >> Eitan whispers, "Hello."

        whisper -l elven "such a snob"
        >> [in elven] Eitan whispers, "Such a snob."

        whisper -t king Hello your majesty.
        >> [to king] Eitan whispers, "Hello your majesty."

        whisper -l dwarven -t Gimli Sup brosef?
        >> [in dwarven to Gimli] Eitan whispers, "Sup, brosef?"
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
            rest = args.full[len(args.tokens[0] + " " + args.tokens[1] + " " + args.tokens[2]
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

    marking = colorfy(marking, 'yellow')

    for e in args.actor.connections:
        if e == args.actor:
            e.sendMessage(marking + colorfy('You whisper, "' + msg + '"', "dark gray"))
        else:
            e.sendMessage(marking + colorfy(args.actor.name + ' whispers, "' + msg + '"', 'dark gray'))

    return True


def who(args):
    """
    See who is connected to the MUSH server.
    syntax: who
    """
    msg = "Currently connected players:\n"
    for e in args.actor.connections:
        msg = msg + "    " + e.name + "\n"
    msg = colorfy(msg, "bright blue")
    args.actor.sendMessage(msg)
    return True


def logout(args):
    """
    Logs you out of the game.
    syntax: logout
    """
    for e in args.actor.connections:
        if e == args.actor:
            args.actor.sendMessage(colorfy("You have quit the session.", "red"))
        else:
            args.actor.sendMessage(colorfy(args.actor.name + " has quit the session.", "red"))
    try:
        args.actor.proxy.running = False
        args.actor.connections.remove(args.actor)
        args.actor.proxy.kill()
    except:
        return True
    return True


def emote(args):
    """
    Perform an emote. Use the ";" token as a placeholder for your name.
    syntax: emote <description containing ; somewhere>

    example:
        emote In a wild abandon, ; breaks into a fit of giggles.
        >> In a wild abandon, Eitan breaks into a fit of giggles.

        emote Smoke drifts upwards from a pipe held between ;'s lips.'
        >> Smoke drifts upwards from a pipe held between ;'s lips.'


    Alternatively, as a shorthand, you may start an emote with the ";" token (no space).

    example:
        ;laughs heartedly.
        >> Eitan laughs heartedly.
    """

    if len(args.tokens) < 2:
        return False

    marking = ">"
    rest = args.full[len(args.name + " "):]

    if not ';' in args.full:
        return False

    rest = rest.replace(';', args.actor.name)

    for e in args.actor.connections:
        e.sendMessage(colorfy(marking + rest, "dark gray"))

    return True


def ooc(args):
    """
    Broadcast out of character text. Anything said here is OOC.
    syntax: ooc <message>

    example:
        ooc Do I need to use a 1d6 or 1d8 for that, DM?
        >> [OOC Justin]: Do I need to use a 1d6 or 1d8 for that, DM?


    Alternatively, as a shorthand, you may start an ooc message with the "*" token (no space).

    example:
        *If you keep metagaming, Justin, I'm going to rip you a new one!
        >> [OOC DM_Eitan]: If you keep metagaming, Justin, I'm going to rip you a new one!
    """

    if len(args.tokens) < 2:
        return False

    marking = "[OOC " + args.actor.name + "]: "
    marking = colorfy(marking, "bright red")

    rest = args.full[len(args.name + " "):]

    for e in args.actor.connections:
        e.sendMessage(marking + rest)

    return True


def roll(args):
    """
    Roll a dice of a specified number of sides. The dice roll is public.
    syntax: roll [-p <purpose>] [-n <quantity>] <sides>

    example:
        roll 20
        >>[DICE] DM_Eitan rolls 1d20.
        >>  18

        roll -p damage -n 2 6
        >>[DICE (damage)] Justin rolls 2d6.
        >>  3
        >>  5


    Alternatively, as a shorthand, you may roll a single dice of N sides with the "3" token (no space).

    example:
        #20
        >>[DICE] DM_Eitan rolls 1d20.
        >>  18
    """
    if len(args.tokens) < 2:
        return False

    # simple case
    num = 0
    sides = 0
    purpose = ""

    if len(args.tokens) == 2:
        num = 1
        try:
            sides = int(args.tokens[1])
        except:
            return False
    else:
        if args.tokens[1] == "-p":
            if not len(args.tokens) >= 4:
                return False
            purpose = args.tokens[2]

            if args.tokens[3] == '-n':
                if not len(args.tokens) >= 6:
                    return False
                try:
                    num = int(args.tokens[4])
                except:
                    return False
            else:
                num = 1

        if args.tokens[1] == "-n":
            if not len(args.tokens) >= 4:
                return False
            try:
                num = int(args.tokens[2])
            except:
                return False

        try:
            sides = int(args.tokens[-1])
        except:
            return False

    marking = "[DICE"
    if purpose != "":
        marking = marking + " (" + purpose + ")"
    marking = marking + "] "
    marking = colorfy(marking, 'bright yellow')

    dice = []
    for i in range(num):
        dice.append(random.randint(1, sides))

    for e in args.actor.connections:
        e.sendMessage(marking + args.actor.name + " rolls " + str(num) + "d" + str(sides) + ".")
        for die in dice:
            e.sendMessage("  " + str(die))

    return True
