import sys
from feynbot.events import EventTree, Event

tree = EventTree("Logging", persistant=True, priority=1000)


@tree.bind("on_ready")
def log_ready(*args, bot, **kwargs) -> None:
    bot.log_green(f"[bold green]{bot.name} is ready![/bold green]")


@tree.bind("on_connect")
def log_connect(*args, bot, **kwargs) -> None:
    bot.log_green(f"[bold green]{bot.name} is connecting...[/bold green]")


@tree.bind("on_error")
def log_error(*args, bot, **kwargs) -> None:
    error = sys.exc_info()
    bot.error(f"Error: {str(error[1])}")
    bot.print(bot.event_trees)
