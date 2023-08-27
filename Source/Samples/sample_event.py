"""An empty event, consider implementing it!"""

from source.event import Event

event_name = "event_name_here"
event = Event(event_name)


@event.handler
def fire(self, bot) -> None:
    """An empty event."""
    bot.console.print(
        f"[italics yellow]{event_name} has not yet been implemented."
        f"[/italics yellow]"
    )
