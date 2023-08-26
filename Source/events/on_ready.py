"""`on_ready` event, fired when the bot is ready after launch."""

from source.events import Event

event_name = "on_ready"
event = Event(event_name)


@event.handler
def fire(self, bot, *args, **kwargs) -> None:
    """Fires the `on_ready` event."""
    bot.console.print(f"[bold green]{bot.name} is ready![/bold green]")
    bot.ready = True
