"""`on_connect' event."""

from source.event import Event

event_name = "on_connect"
event = Event(event_name)


@event.handler
def fire(self, bot, *args, **kwargs) -> None:
    """Fires the `on_connect` event."""
    bot.console.print(f"[bold green]{bot.name} connected.[/bold green]")
