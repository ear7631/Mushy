import commands
import namedtuple

CommandArgs = namedtuple.namedtuple('CommandArgs', 'name tokens full actor')
commandFunctions = {}

if len(commandFunctions) == 0:
    #commandFunctions["look"] = (commands.look)
    commandFunctions["say"] = (commands.say)
    commandFunctions["logout"] = (commands.logout)
    commandFunctions["help"] = (commands.help)
    commandFunctions["who"] = (commands.who)
    commandFunctions["pm"] = (commands.pm)
    commandFunctions["whisper"] = (commands.whisper)
    commandFunctions["emote"] = (commands.emote)
    commandFunctions["ooc"] = (commands.ooc)
    commandFunctions["roll"] = (commands.roll)


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
        new_tokens = ["roll", args.tokens[0][1:]]
        new_full = "roll " + args.full[1:]

        newargs = CommandArgs(name=new_name, tokens=new_tokens, full=new_full, actor=args.actor)
        return newargs

    return args
