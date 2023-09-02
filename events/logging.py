import sys
from Feynbot.events import EventTree

tree = EventTree("Logging", persistent=True, priority=100)


@tree.bind("on_socket_event_type", "LogEvent")
def log_event(bot, **_) -> None:
    pass


@tree.bind("on_ready", "LogReady")
def log_ready(bot, **_) -> None:
    bot.log(f"[bold green]{bot.name} is ready![/bold green]")


@tree.bind("on_connect", "LogConnect")
def log_connect(bot, **_) -> None:
    bot.log(f"[bold green]{bot.name} is connecting...[/bold green]")


@tree.bind("on_error", "LogError")
def log_error(bot, **_) -> None:
    error = sys.exc_info()
    bot.error(f"Error: {str(error[1])}", stack_offset=2)
    # bot.print(repr(bot.event_trees))


@tree.bind("on_guild_available", "LogGuildAvailable")
def log_guild_available(bot, **_) -> None:
    bot.log("[green]Guild available.[/green]")


@tree.bind("on_interaction", "LogInteraction")
def log_interaction(bot, **_) -> None:
    bot.log("Interaction received.")


@tree.bind("on_app_command_completion", "LogInteractionCompleted")
def log_interaction_completed(bot, **_) -> None:
    bot.log("Interaction completed.")
