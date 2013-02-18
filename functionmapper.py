import commands

commandFunctions = {}

if len(commandFunctions) == 0:
    #commandFunctions["look"] = (commands.look)
    commandFunctions["say"] = (commands.say)
    commandFunctions["logout"] = (commands.logout)
    commandFunctions["help"] = (commands.help)
    commandFunctions["who"] = (commands.who)
    commandFunctions["pm"] = (commands.pm)
    commandFunctions["whisper"] = (commands.whisper)
