"""`on_message` event."""

from source.events import Event

event_name = "on_message"
event = Event(event_name)


@event.handler
def fire(self, bot, message) -> None:
    """Fires the `on_message` event."""
    bot.console.print("Message recieved!")
