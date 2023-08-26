"""An event override."""

from source.event import Event


class EventOverride(Event):
    """An event override."""

    def __init__(self, *args, **kwargs) -> None:
        self.terminal = kwargs.get("terminal", False)
        super().__init__(*args, **kwargs)
