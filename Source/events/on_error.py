"""`on_error` event, fired when the bot raises an error."""

import sys

from source.events import Event

event_name = "on_error"
event = Event(event_name)


@event.handler
def fire(self, bot, method, *args, **kwargs) -> None:
    """Fires the `on_error` event."""
    error_type, error, traceback = sys.exc_info()
    bot.console.print(
        f"[bold red]An error has occured in `{method}`.\n"
        f"{error_type}: {error}\n"
        f"{traceback}[/bold red]"
    )
