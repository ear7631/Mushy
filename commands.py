import sys
import inspect
import random
import namedtuple
import functionmapper
import commandparser
import entity
from colorer import colors as swatch
from colorer import colorfy

CommandArgs = namedtuple.namedtuple('CommandArgs', 'name tokens full actor')

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
            subject - the subject or command which you want to check for help
    """
    if len(args.tokens) == 1:
        commands = functionmapper.commandFunctions.keys()
        commands.sort()

        msg = "    "
        i = 0
        for command in commands:
            msg = msg + command + (' ' * (15 - len(command)))
            i = (i + 1) % 4
            if i == 0:
                msg = msg + "\n    "

        args.actor.sendMessage("There are help files on the following commands.\nType help <command> for details.")
        args.actor.sendMessage(msg)

        return True

    helpFunctionName = args.tokens[1]
    functions = inspect.getmembers(sys.modules[__name__], inspect.isfunction)
    docstring = None
    for functionName, function in functions:
        if functionName == helpFunctionName:
            docstring = function.__doc__

    if docstring is None:
        args.actor.sendMessage("There is no helpfile for " + args.tokens[1] + ".")
    else:
        prelude = "help file for: " + args.tokens[1] + "\n" + ("-" * len("help file for: " + args.tokens[1]))
        prelude = colorfy(prelude, 'green')
        args.actor.sendMessage(prelude + docstring)

    return True


def say(args):
    """
    Say something out loud, in character. Unless otherwise specified, things
    are said in common.

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
    for e in args.actor.instance.connections:
        if e == args.actor:
            e.sendMessage(marking + colorfy('You say, "' + msg + '"', "white"))
        else:
            e.sendMessage(marking + colorfy(args.actor.name + ' says, "' + msg + '"', "white"))

    return True


def pm(args):
    """
    Give a private message to someone, out of character. Other people
    cannot see these messages.
    Note: This is OOC and shouldn't be abused!

    syntax: pm <player> <message>
            player - target of the pm
            message - what you would like to say privately
    """
    if not len(args.tokens) >= 3:
        return False

    for e in args.actor.instance.connections:
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

    for e in args.actor.instance.connections:
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
    msg = colorfy("Currently connected players:\n", "bright blue")
    for e in args.actor.instance.connections:
        name = colorfy(e.name, "bright blue")
        if e.dm:
            name = name + colorfy(" (DM)", "bright red")
        msg = msg + "    " + name + "\n"
    args.actor.sendMessage(msg)
    return True


def logout(args):
    """
    Logs you out of the game.

    syntax: logout
    """
    for e in args.actor.instance.connections:
        if e == args.actor:
            args.actor.sendMessage(colorfy("[SERVER] You have quit the session.", "bright yellow"))
        else:
            e.sendMessage(colorfy("[SERVER] " + args.actor.name + " has quit the session.", "bright yellow"))
    try:
        args.actor.proxy.running = False
        args.actor.instance.connections.remove(args.actor)
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


    Alternatively, as a shorthand, you may start an emote with the ";" token
    (no space).

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

    for e in args.actor.instance.connections:
        e.sendMessage(colorfy(marking + rest, "dark gray"))

    return True


def ooc(args):
    """
    Broadcast out of character text. Anything said here is OOC.

    syntax: ooc <message>

    example:
        ooc Do I need to use a 1d6 or 1d8 for that, DM?
        >> [OOC Justin]: Do I need to use a 1d6 or 1d8 for that, DM?


    Alternatively, as a shorthand, you may start an ooc message with the
    "*" token (no space).

    example:
        *If you keep metagaming, I'm going to rip you a new one!
        >> [OOC DM_Eitan]: If you keep metagaming, I'm going to kill you!
    """

    if len(args.tokens) < 2:
        return False

    name = args.actor.name
    if args.actor.dm:
        name = name + " (DM)"
    marking = "[OOC " + name + "]: "
    marking = colorfy(marking, "bright red")

    rest = args.full[len(args.name + " "):]

    for e in args.actor.instance.connections:
        e.sendMessage(marking + rest)

    return True


def roll(args):
    """
    Roll a dice of a specified number of sides. The dice roll is public.

    syntax: roll <number>d<sides> [reason]

    example:
        roll 1d20
        >>[DICE] DM_Eitan rolls 1d20.
        >>  18

        roll 2d6 damage
        >>[DICE (damage)] Justin rolls 2d6.
        >>  3
        >>  5


    Alternatively, as a shorthand, you may roll a single die of N sides
    with no specified purpose with the "#" token (no space).

    example:
        #20
        >>[DICE] DM_Eitan rolls 1d20.
        >>  18


    Rolls can also be kept hidden from others. To do this, use the
    command "hroll" instead of "roll".

    example:
        hroll 1d20
    """
    if len(args.tokens) < 2:
        return False

    # simple case
    num = 0
    sides = 0
    purpose = ""

    dice = args.tokens[1].split('d')
    if len(dice) != 2:
        return False

    try:
        num = int(dice[0])
        sides = int(dice[1])
    except:
        return False

    visible = True
    if args.tokens[0] == 'hroll':
        visible = False

    purpose = args.full[len(args.tokens[0] + " " + args.tokens[1] + " "):]

    marking = "[DICE"
    if purpose != "":
        marking = marking + " (" + purpose + ")"
    marking = marking + "] "
    marking = colorfy(marking, 'bright yellow')

    dice = []
    for i in range(num):
        dice.append(random.randint(1, sides))

    for e in args.actor.instance.connections:
        if visible or e == args.actor:
            e.sendMessage(marking + args.actor.name + " rolls " + str(num) + "d" + str(sides) + ".")
            for die in dice:
                e.sendMessage("  " + str(die))

    return True


def mask(args):
    """
    Mask a command as if you were another character. Don't abuse this, DM!

    syntax: mask <name> <command>
            name - the name of the entity you wish to do something as
            command - the regular command string as if you were entering it
                      as normal

    example:
        mask King say Welcome, my subjects, to my domain!
        >> King says, "Welcome, my subjects, to my domain!"

        mask John ;bows with a flourish.
        >> John bows with a flourish.

    Alternatively, as a shorthand, you may mask as another person by using
    the "$" token (no space).

    example:
        $Nameless say Who... who am I?
        >> Nameless says, "Who... who am I?"
    """

    if len(args.tokens) < 3:
        return False

    if not args.actor.dm:
        args.actor.sendMessage("Whoa there... This is a DM power! Bad!")
        return True

    husk = entity.Entity(None, args.tokens[1][0].upper() + args.tokens[1][1:], args.actor.instance)
    new_name = args.tokens[2]
    new_tokens = args.tokens[2:]
    new_full = args.full[len(args.tokens[0] + " " + args.tokens[1] + " "):]
    new_args = CommandArgs(name=new_name, tokens=new_tokens, full=new_full, actor=husk)

    commandparser.queueCommand(new_args)
    return True


def display(args):
    """
    Display text in a color of your choosing without any "tags". Basically, use
    this as an immersion tool for typing descriptions.

    The DM may want to display text to only a particular player, and not want
    the rest of the group to be aware OOCly, allowing for better roleplay.

    syntax: display [-c color] [-t target] <text>
            color - the color which you want the text to display in
            target - the target of the text
            text - the text to display

    To view a list of colors, type "colors".

    example:
        display -c BRED The flame licks at the prisoner's cheek.
        >> \033[1;31mThe flame licks at the prisoner's cheek.\033[0m

        display -c YELLOW -t Justin Spiritual voices wail in your mind...
        >> \033[0;33mSpiritual voices wail in your mind...\033[0m


    Alternatively, as a shorthand, you may display text using the "@" token
    (no space). By doing this, the first argument is the color itself, and
    no target is specified.

    example:
        @RED Blood trickles down the victim's nose.
        >> \033[0;31mBlood trickles down the victim's nose.\033[0m
    """

    if len(args.tokens) < 2:
        return False

    color = "default"
    target = None
    if args.tokens[1] == '-c':
        if len(args.tokens) < 4:
            return False

        color = args.tokens[2].lower()
        if not color in swatch:
            return False

        rest = args.full[len(args.tokens[0] + " " + args.tokens[1] + " " + args.tokens[2] + " "):]

        if args.tokens[3] == '-t':
            if len(args.tokens) < 6:
                return False
            target_name = args.tokens[4]

            for e in args.actor.instance.connections:
                if e.name.lower() == target_name.lower():
                    target = e

            if target == None:
                return False
            rest = rest[len(args.tokens[3] + " " + args.tokens[4] + " "):]
    else:
        rest = args.full[len(args.tokens[0] + " "):]

    rest = colorfy(rest, color)

    if target != None:
        target.sendMessage(rest)
    else:
        for e in args.actor.instance.connections:
            e.sendMessage(rest)

    return True


def status(args):
    """
    Set your status. This is meant to be an in-character roleplay tool. For
    example, after being struck with an arrow, you may want to set your status
    to indicate that you are injured. Treat these as an emoted "state".

    Setting these is not quiet, and will indicate to the group what is going on
    as an emote. Take care to phrase the status as a passive state. It sounds
    best if you are able to say "Soandso is..." prior to a status.

    If you specify status as "clear", it will clear your status silently.

    syntax: status <status>

    example:
        status Limping behind the group, using his staff as a cane.
        >> Eitan is limping behind the group, using his staff as a cane.

        >> glance Eitan
        >> Eitan is limping behind the group, using his staff as a cane.

        >> status clear
    """
    if len(args.tokens) < 2:
        return False

    if args.tokens[1] == 'clear':
        args.actor.status = ""
        args.actor.sendMessage("You've cleared your status.")
        return True

    status = args.full[len(args.tokens[0] + " "):]
    status = status[0].upper() + status[1:]
    if status[-1] not in (".", "!", "?"):
        status = status + "."

    args.actor.status = status

    status = status[0].lower() + status[1:]

    for e in args.actor.instance.connections:
        if e == args.actor:
            e.sendMessage(colorfy(">You are " + status, "dark gray"))
        else:
            e.sendMessage(colorfy(">" + args.actor.name + " is " + status, "dark gray"))

    return True


def glance(args):
    """
    Glance at another player to see their set status.

    syntax: glance <player>
    """

    if len(args.tokens) < 2:
        return False

    for e in args.actor.instance.connections:
        if e.name.lower() == args.tokens[1].lower():
            args.actor.sendMessage("You glance at " + e.name + ".")
            if e.status == "":
                return True
            status = e.status[0].lower() + e.status[1:]
            args.actor.sendMessage("  " + e.name + " is " + colorfy(status, "dark gray"))
            return True

    args.actor.sendMessage('There is no player "' + args.tokens[1] + '" here.')
    return True


def examine(args):
    pass


def colors(args):
    """
    Displays a list of the colors available for use in certain commands.

    syntax: colors
    """

    msg = """    List of colors:
        \033[1;34mDEFAULT\033[0m
        \033[1;37mWHITE\033[0m
        \033[0;37mBGRAY\033[0m
        \033[1;30mDGRAY\033[0m
        \033[0;30mBLACK\033[0m
        \033[0;34mBLUE\033[0m
        \033[1;34mBBLUE\033[0m
        \033[0;36mCYAN\033[0m
        \033[1;36mBCYAN\033[0m
        \033[0;32mGREEN\033[0m
        \033[1;32mBGREEN\033[0m
        \033[0;33mYELLOW\033[0m
        \033[1;33mBYELLOW\033[0m
        \033[0;31mRED\033[0m
        \033[1;31mBRED\033[0m
        \033[0;35mPURPLE\033[0m
        \033[1;35mBPURPLE\033[0m
    """
    args.actor.sendMessage(msg)
    return True


def paint(args):
    """
    A DM may "paint" items of interest into the session area. Three things
    may be painted in a color of their choosing:
        "Scene" title - The name of where you are
        "Scene" body - The description of where you are
        "Object" - A particular item of interest that can be looked at

    Players may look at the scene by using the "look" command with no
    arguments. Players may also look at an object by specifying the
    object tag.

    syntax: paint [-c color] <title|body> <description>
            paint [-c color] <object> <tag> <description>

            color - the color which you want the text to display in
            description - what the thing looks like
            tag - the identifier to use when "looking" at an object

    To view a list of colors, type "colors".

    example:
        paint -c BRED title Inferno Cave
        paint body Lava swirls around burning stone in a river of red.
        paint -c RED object flame A pillar of flame burns
                                             in the center of the cave.
    """
    if len(args.tokens) < 3:
        return False

    if not args.actor.dm:
        return False

    color = ""
    tokens = args.tokens
    snipped = 0

    stage = args.actor.instance.stage

    if tokens[1] == '-c':
        if len(tokens) < 5:
            return False

        color = tokens[2].lower()
        if not color in swatch:
            return False

        snipped = len(tokens[1] + " " + tokens[2] + " ")
        tokens = [tokens[0]] + tokens[3:]
    else:
        color = "default"

    if tokens[1] == "title":
        stage.paintSceneTitle(colorfy(args.full[snipped + len(tokens[0] + " " + tokens[1] + " "):], color))
        for e in args.actor.instance.connections:
            e.sendMessage(colorfy(args.actor.name + " paints a scene.", "bright red"))

    elif tokens[1] == "body":
        stage.paintSceneBody(colorfy(args.full[snipped + len(tokens[0] + " " + tokens[1] + " "):], color))
        for e in args.actor.instance.connections:
            e.sendMessage(colorfy(args.actor.name + " paints a scene.", "bright red"))

    elif tokens[1] == "object":
        if len(tokens) < 4:
            return False
        stage.paintObject(tokens[2], colorfy(args.full[snipped + len(tokens[0] + " " + tokens[1] + " " + tokens[2] + " "):], color))
        for e in args.actor.instance.connections:
            e.sendMessage(colorfy(args.actor.name + " paints a " + tokens[2] + ".", "bright red"))

    else:
        return False

    return True


def erase(args):
    """
    A DM may erase a painted part of the scene, or a painted object.

    syntax: erase scene
            erase object <tag>

            tag - the identifier to use when "looking" at an object

    To view a list of objects in the scene, simply use the look command.
    """
    if len(args.tokens) < 2:
        return False

    if not args.actor.dm:
        return False

    stage = args.actor.instance.stage

    if args.tokens[1] == "scene":
        stage.wipeScene()
        for e in args.actor.instance.connections:
            e.sendMessage(colorfy(args.actor.name + " erases the scene.", "bright red"))

    elif args.tokens[1] == "object":
        if len(args.tokens) < 3:
            return False

        if args.tokens[2].lower() in stage.objects:
            stage.eraseObject(args.tokens[2])
            for e in args.actor.instance.connections:
                e.sendMessage(colorfy(args.actor.name + " erases the " + args.tokens[2] + ".", "bright red"))

    else:
        return False

    return True


def wipe(args):
    """
    A DM may wipe an entire scene and all objects painted in it.

    syntax: wipe
    """
    if not args.actor.dm:
        return False

    stage = args.actor.instance.stage
    stage.wipeScene()
    stage.wipeObjects()

    for e in args.actor.instance.connections:
        e.sendMessage(colorfy(args.actor.name + " wipes the whole scene.", "bright red"))

    return True


def look(args):
    """
    Allows a player to look at a scene, or a particular painted object.

    syntax: look [tag]
            tag - the identifier to use when "looking" at an object

    To view a list of objects in the scene, simply use look without arguments.
    """
    stage = args.actor.instance.stage

    if len(args.tokens) == 1:
        scene = stage.viewScene()
        if scene == "":
            args.actor.sendMessage("The scene is blank.")
        else:
            args.actor.sendMessage(scene)
        return True

    description = stage.viewObject(args.tokens[1])
    if description == "":
        args.actor.sendMessage('There is no "' + args.tokens[1] + '" in the scene.')
    else:
        args.actor.sendMessage(description)
    return True


def tally(args):
    """
    A player or DM may create a generic "tally" to keep track of something.
    Tallies may be saved (persistent) or not (removed after logout).

    syntax: tally <subcommand> <tag>

    List of subcommands and syntax:
        Add:        tally add <tag> [amount]
        Change:     tally change <tag> <value>
        Check:      tally check [tag]
        Create:     tally create <tag> [initial]
        Destroy:    tally destroy <tag>
        Remove:     tally remove <tag> [amount]
        Share:      tally share <tag> [entity]
        Save:       tally save <tag>

    There are a few shorthand commands for your convenience. You may increment
    or decrement a tally easily using the following syntax:
        tally <tag> ++
        tally <tag> --

    You may also check the values for all your tallies by simply entering
    the command 'tallies'.
    """

    if len(args.tokens) < 3:
        if len(args.tokens) == 1:
            if args.tokens[0] != 'tallies':
                return False
        elif len(args.tokens) == 2:
            if args.tokens[1] != 'check':
                return False
        else:
            return False

    tokens = args.tokens

    # tallies substitution
    if args.tokens[0] == 'tallies':
        tokens = ['tally', 'check']

    # shorthand substitution
    elif '++' in args.full or '--' in args.full:
        if tokens[2] == '++':
            tokens = ['tally', 'add', tokens[1]]
        elif tokens[2] == '--':
            tokens = ['tally', 'remove', tokens[1]]

    subcommand = tokens[1]
    tag = ''
    if len(tokens) > 2:
        tag = tokens[2]

    if subcommand == 'create':
        if tag in args.actor.tallies:
            args.actor.sendMessage("Tally " + tag + " already exists.")
        else:
            value = 0
            if len(tokens) > 3:
                value = int(tokens[3])
            args.actor.tallies[tag] = value

    elif subcommand == 'destroy':
        if tag in args.actor.tallies:
            del args.actor.tallies[tag]
        else:
            args.actor.sendMessage("Tally " + tag + " does not exist.")

    elif subcommand == 'add':
        if tag in args.actor.tallies:
            value = 1
            if len(tokens) > 3:
                value = int(tokens[3])
            args.actor.tallies[tag] += value
        else:
            args.actor.sendMessage("Tally " + tag + " does not exist.")

    elif subcommand == 'remove':
        if tag in args.actor.tallies:
            value = 1
            if len(tokens) > 3:
                try:
                    value = int(tokens[3])
                except:
                    return False
            args.actor.tallies[tag] -= value
        else:
            args.actor.sendMessage("Tally " + tag + " does not exist.")

    elif subcommand == 'change':
        if tag in args.actor.tallies:
            if len(tokens) > 3:
                try:
                    value = int(tokens[3])
                except:
                    return False
                args.actor.tallies[tag] = value
            else:
                args.actor.sendMessage("Usage: tally change <tag> <amount>")
        else:
            args.actor.sendMessage("Tally " + tag + " does not exist.")

    elif subcommand == 'share' or subcommand == 'show' or subcommand == 'display':
        if tag in args.actor.tallies:
            if len(tokens) > 3:
                for e in args.actor.instance.connections:
                    if e.name.lower() == tokens[3].lower():
                        e.sendMessage(args.actor.name + " shares a tally with you: [" +
                                      colorfy(tag, 'white') + ": " + colorfy(str(args.actor.tallies[tag]), 'cyan') + "]")
                        args.actor.sendMessage("You share tally " + tag + " with " + tokens[3] + ": [" +
                                               colorfy(tag, 'white') + ": " + colorfy(str(args.actor.tallies[tag]), 'cyan') + "]")
            else:
                for e in args.actor.instance.connections:
                    e.sendMessage(args.actor.name + " shares a tally: [" +
                                  colorfy(tag, 'white') + ": " + colorfy(str(args.actor.tallies[tag]), 'cyan') + "]")
        else:
            args.actor.sendMessage("Tally " + tag + " does not exist.")

    elif subcommand == 'save':
        args.actor.sendMessage("Tally saving is not yet implemented.")

    elif subcommand == 'check' or subcommand == 'list':
        if len(tokens) > 2:
            tag = tokens[2]
            if tag in args.actor.tallies:
                args.actor.sendMessage("The value of tally " + tag + " is " + colorfy(str(args.actor.tallies[tag]), 'cyan') + ".")
            else:
                args.actor.sendMessage("Tally " + tag + " does not exist.")
        else:
            keys = args.actor.tallies.keys()
            if len(keys) == 0:
                args.actor.sendMessage("You have no tallies.")
                return True

            args.actor.sendMessage("------TALLIES------")
            sorted(keys)
            for key in keys:
                args.actor.sendMessage("    [" + colorfy(key, 'white') + ": " +
                                       colorfy(str(args.actor.tallies[key]), 'cyan') + "]")

    else:
        return False

    return True


def bag(args):
    """
    A player or DM may create a generic "bag" to keep track of items.
    Bags may be saved (persistent) or not (removed after logout).

    syntax: bag <subcommand> <tag>

    List of subcommands and syntax:
        Add:        bag add <tag> <item>
        Check:      bag check [tag]
        Create:     bag create <tag> [initial]
        Empty:      bag empty <tag>
        Destroy:    bag destroy <tag>
        Remove:     bag remove <tag> <item>
        Share:      bag share <tag | all> [entity]
        Save:       bag save <tag>


    You may also check the contents for all your bags by simply entering
    the command 'bags'.
    """

    if len(args.tokens) < 3:
        if len(args.tokens) == 1:
            if args.tokens[0] != 'bags':
                return False
        elif len(args.tokens) == 2:
            if args.tokens[1] != 'check':
                return False
        else:
            return False

    tokens = args.tokens

    # bags substitution
    if args.tokens[0] == 'bags':
        tokens = ['bag', 'check']

    subcommand = tokens[1]
    tag = ''
    if len(tokens) > 2:
        tag = tokens[2]

    if subcommand == 'create':
        if tag in args.actor.bags:
            args.actor.sendMessage("Bag " + tag + " already exists.")
        else:
            args.actor.bags[tag] = []

    elif subcommand == 'destroy':
        if tag in args.actor.bags:
            del args.actor.bags[tag]
        else:
            args.actor.sendMessage("Bag " + tag + " does not exist.")

    elif subcommand == 'add':
        if len(tokens) < 4:
            args.actor.sendMessage("Usage: bag add <tag> <item>")
        elif tag in args.actor.bags:
            item = tokens[3]
            args.actor.bags[tag].append(item)
        else:
            args.actor.sendMessage("Bag " + tag + " does not exist.")

    elif subcommand == 'remove':
        if len(tokens) < 4:
            args.actor.sendMessage("Usage: bag remove <tag> <item>")
        elif tag in args.actor.bags:
            item = tokens[3]
            if item in args.actor.bags[tag]:
                args.actor.bags.remove(item)
            else:
                args.actor.sendMessage("Bag " + tag + " does not contain item " + tokens[3] + ".")
        else:
            args.actor.sendMessage("Bag " + tag + " does not exist.")

    elif subcommand == 'empty':
        if tag in args.actor.bags:
            args.actor.bags[tag] = []
        else:
            args.actor.sendMessage("Bag " + tag + " does not exist.")

    elif subcommand == 'share' or subcommand == 'show' or subcommand == 'display':
        keys = args.actor.bags.keys()
        if len(keys) == 0:
            args.actor.sendMessage("You have no bags.")
            return True
        sorted(keys)

        if tag == 'all':
            if len(tokens) > 3:
                for e in args.actor.instance.connections:
                    if e.name.lower() == tokens[3].lower():
                        e.sendMessage(args.actor.name + " shares some bags with you: ")
                        args.actor.sendMessage("You share your bags with " + tokens[3] + ".")
                        for key in keys:
                            e.sendMessage("    " + key + ": " + str(args.actor.bags[key]))
            else:
                args.actor.sendMessage("You share your bags.")
                for e in args.actor.instance.connections:
                    if e.name.lower() == args.actor.name.lower():
                        continue
                    e.sendMessage(args.actor.name + " shares some bags:")
                    for key in keys:
                        e.sendMessage("    " + key + ": " + str(args.actor.bags[key]))
        elif tag in args.actor.bags:
            if len(tokens) > 3:
                for e in args.actor.instance.connections:
                    if e.name.lower() == tokens[3].lower():
                        e.sendMessage(args.actor.name + " shares a bag (" + tag + ") with you: " + str(args.actor.bags[tag]))
                        args.actor.sendMessage("You share a bag (" + tag + ") with " + tokens[3] + ".")
            else:
                for e in args.actor.instance.connections:
                    e.sendMessage(args.actor.name + " shares a bag (" + tag + "): " + str(args.actor.bags[tag]))
        else:
            args.actor.sendMessage("Bag " + tag + " does not exist.")

    elif subcommand == 'save':
        args.actor.sendMessage("Bag saving is not yet implemented.")

    elif subcommand == 'check' or subcommand == 'list':
        if len(tokens) > 2:
            tag = tokens[2]
            if tag in args.actor.bags:
                args.actor.sendMessage("The bag (" + tag + ") contains the following items: " + str(args.actor.bags[tag]))
            else:
                args.actor.sendMessage("Bag " + tag + " does not exist.")
        else:
            keys = args.actor.bags.keys()
            if len(keys) == 0:
                args.actor.sendMessage("You have no bags.")
                return True

            args.actor.sendMessage("------BAGS------")
            sorted(keys)
            for key in keys:
                args.actor.sendMessage("    " + key + ": " + str(args.actor.bags[key]))

    else:
        return False

    return True

