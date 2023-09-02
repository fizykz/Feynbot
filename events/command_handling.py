from Feynbot.events import EventTree

tree = EventTree("CommandHandling", persistent=True, priority=75)


@tree.bind("on_guild_available", "SyncGuildCommands")
async def log_ready(bot, **_) -> None:
    bot.log("Syncing guild commands...")
    await bot.sync_commands()
    bot.log("Guild commands synced.")
