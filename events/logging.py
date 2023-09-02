import sys
from Feynbot.events import EventTree

tree = EventTree("Logging", persistent=True, priority=1000)


@tree.bind("on_ready")
def log_ready(bot, **_) -> None:
    bot.log_green(f"[bold green]{bot.name} is ready![/bold green]")


@tree.bind("on_connect")
def log_connect(bot, **_) -> None:
    bot.log_green(f"[bold green]{bot.name} is connecting...[/bold green]")


@tree.bind("on_error")
def log_error(bot, **_) -> None:
    error = sys.exc_info()
    bot.error(f"Error: {str(error[1])}")
    bot.print(bot.event_trees)
