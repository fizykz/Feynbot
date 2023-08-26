"""`on_error` event, fired when the bot raises an error."""

from source.event import Event

event_name = "on_error"
event = Event(event_name)


@event.handler
def fire(self, bot) -> None:
    """Fires the `on_error` event."""
    bot.console.print("[bold red]An error has occured.[/bold red]")
