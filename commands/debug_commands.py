from Feynbot.commands import CommandTree

tree = CommandTree("DebugCommands")


@tree.bind("ping", "Ping", description="Pong!")
def ping(bot, **_):
    bot.log("Pong!")
