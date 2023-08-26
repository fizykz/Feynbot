"""An event."""

from typing import Any, Callable


class Event:
    """An event."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.fire: Callable = lambda self, bot, *a, **kwa: bot.console.print(
            f"[yellow]Event {self.name} not implemented!\n"
            f"#Args: {len(a)}   #Kwargs: {len(kwa)}[/yellow]"
        )
        self.get_override_ids: Callable = lambda *args, **kwargs: None

    def overrides(self, function: Callable[..., list[int]]) -> None:
        """Binds a function to acquire relevant override IDs."""
        self.get_override_ids = function

    def handler(self, function: Callable) -> None:
        """Fire the event."""
        self.fire = function

    def __call__(self, bot, *args: Any, **kwargs: Any) -> Any:
        """Call the event."""
        return self.fire(self, bot, *args, **kwargs)


class EventOverride(Event):
    """An event override."""

    def __init__(self, *args, **kwargs) -> None:
        self.terminal = kwargs.get("terminal", False)
        super().__init__(*args, **kwargs)
