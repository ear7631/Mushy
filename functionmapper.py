from commands import *
import namedtuple

CommandArgs = namedtuple.namedtuple('CommandArgs', 'name tokens full actor')
commandFunctions = {}

# On first load, initialize the function mappings
if len(commandFunctions) == 0:
    commandFunctions["say"] = say
    commandFunctions["logout"] = logout
    commandFunctions["help"] = help
    commandFunctions["who"] = who
    commandFunctions["pm"] = pm
    commandFunctions["whisper"] = whisper
    commandFunctions["emote"] = emote
    commandFunctions["ooc"] = ooc
    commandFunctions["roll"] = roll
    commandFunctions["hroll"] = roll
    commandFunctions["display"] = display
    commandFunctions["mask"] = mask
    commandFunctions["status"] = status
    commandFunctions["glance"] = glance
    commandFunctions["colors"] = colors
    commandFunctions["paint"] = paint
    commandFunctions["sculpt"] = sculpt
    commandFunctions["brush"] = brush
    commandFunctions["wipe"] = wipe
    commandFunctions["look"] = look
    commandFunctions["tally"] = tally
    commandFunctions["tallies"] = tally
    commandFunctions["bag"] = bag
    commandFunctions["bags"] = bag
    commandFunctions["save"] = save
    commandFunctions["desc"] = description
    commandFunctions["description"] = description
    commandFunctions["exa"] = examine
    commandFunctions["examine"] = examine
    commandFunctions["hastepaste"] = hastepaste
    commandFunctions["test"] = test


def shorthandHandler(args):
    if len(args.tokens) < 1:
        return args

    if len(args.full) < 2:
        return args

    if args.name[0] == ';':
        new_name = "emote"
        new_tokens = ["emote", ";", args.tokens[0][1:]] + args.tokens[1:]
        new_full = "emote ; " + args.full[1:]

        newargs = CommandArgs(name=new_name, tokens=new_tokens, full=new_full, actor=args.actor)
        return newargs

    elif args.name[0] == "'":
        new_name = "say"
        new_tokens = ["say", args.tokens[0][1:]] + args.tokens[1:]
        new_full = "say " + args.full[1:]

        newargs = CommandArgs(name=new_name, tokens=new_tokens, full=new_full, actor=args.actor)
        return newargs

    elif args.name[0] == "*":
        new_name = "ooc"
        new_tokens = ["ooc", args.tokens[0][1:]] + args.tokens[1:]
        new_full = "ooc " + args.full[1:]

        newargs = CommandArgs(name=new_name, tokens=new_tokens, full=new_full, actor=args.actor)
        return newargs

    elif args.name[0] == "#":
        new_name = "roll"
        new_tokens = ["roll", '1d' + args.tokens[0][1:]]
        new_full = "roll 1d" + args.tokens[0][1:]

        newargs = CommandArgs(name=new_name, tokens=new_tokens, full=new_full, actor=args.actor)
        return newargs

    elif args.name[0] == "$":
        new_name = "mask"
        new_tokens = ["mask", args.tokens[0][1:]] + args.tokens[1:]
        new_full = "mask " + args.full[1:]

        newargs = CommandArgs(name=new_name, tokens=new_tokens, full=new_full, actor=args.actor)
        return newargs

    elif args.name[0] == "@":
        new_name = "display"
        new_tokens = ["display", "-c", args.tokens[0][1:]] + args.tokens[1:]
        new_full = "display -c " + args.full[1:]

        newargs = CommandArgs(name=new_name, tokens=new_tokens, full=new_full, actor=args.actor)
        return newargs

    return args
