"""Command & Event handler for Feynbot.  `discord.py` listens for events and
calls the respective function here.  In addition it pulls event and command
data from the other directories in this package."""

import os
import importlib
from typing import Callable, Optional
import regex as re

from discord import Client

from source.events import Event, EventOverride


EVENTS = "./source/events/"
EVENT_OVERRIDES = "./source/event_overrides/"
COMMANDS = "./source/Commands/"
COMMAND_OVERRIDES = "./source/command_overrides/"


class HandlerBot(Client):
    """Command & Event handler for Feynbot."""

    def __init__(self, bot, *args, **kwargs) -> None:
        self.console = bot.console
        self.events: dict[str, Event] = {}
        self.event_overrides: dict[str, dict[str, EventOverride]] = {}
        self.commands = {}
        self.command_overrides = {}

        self.event_list = kwargs.pop("event_list", None)
        if self.event_list is None:
            raise ValueError(
                "Event list not provided!  Did you forget to set up "
                "`config.json`?  (Use `configure.py` to generate)"
            )
        self.event_list: dict[str, bool] = self.event_list

        self.load()

        def get_handler(self, event_name) -> Callable:
            async def handler(*args, **kwargs) -> None:
                await self.fire_event(event_name, *args, **kwargs)

            handler.__name__ = event_name + "_handler"
            return handler

        for event, enabled in self.event_list.items():
            if enabled:
                setattr(self, event, get_handler(self, event))

        super().__init__(*args, **kwargs)

    async def fire_event(self, event_name: str, *args, **kwargs) -> None:
        """Fires an events after being passed from `discord.py`.  This method
        will find the event methods, check for overrides, permissions, and
        then fire those functions as needed."""
        events = self.get_events(event_name)
        # TODO: Impement checking, permissions, overrides
        for event in events:
            event(self, *args, **kwargs)

    def get_events(self, event_name: str) -> list[Event]:
        """Gets the events for the given event name, accounting for overrides
        and terminals."""
        event = self.get_event(event_name)
        # TODO: Implement event overrides
        return [event]

    def get_event(self, event_name: str) -> Event:
        """Returns the standard event for a given event name."""
        event = self.events.get(event_name)
        if not event:
            raise IndexError(
                f"Default Event `{event_name}` not found!  Make sure the file "
                f"is in the `events` directory and is named `{event_name}.py`."
            )
        return event

    def get_event_override(
        self, event_name: str, override_ids: list[int]
    ) -> list[Optional[EventOverride]]:
        """Returns all event overrides for a given event name and list of
        override IDs.  These override IDs are a list of relevant integers for
        the event.  For example, a message event would have possibly a guild
        ID, channel ID, and author ID."""
        overrides_set = self.event_overrides.get(event_name, {})
        overrides = []
        for override_id, event in overrides_set.items():
            if override_id in override_ids:
                overrides.append(event)
        return overrides

    def reload(self) -> None:
        """Reloads all commands and events, even reloading the modules."""
        # TODO: Implement with reload command from importlib
        for event in self.events:
            pass
        for set in self.event_overrides:
            for event in set:
                pass

        for command in self.commands:
            pass
        for set in self.command_overrides:
            for command in set:
                pass

    def load(self) -> None:
        """Finds and loads all commands and events, registering them with the
        bot.
        """
        self.load_events()
        self.load_event_overrides()
        # self.load_commands()
        # self.load_command_overrides()

    def load_events(self) -> None:
        """Loads all events from the events directory."""
        template = "event.py"
        events: dict[str, Event] = {}
        # Iterate over every event
        for event in os.listdir(EVENTS):
            if event == template:
                continue
            if not event.endswith(".py"):
                continue
            name = event[:-3]
            module = importlib.import_module(f"source.events.{name}")
            events[name] = module.event
        self.events = events

    def load_event_overrides(self) -> None:
        """Loads all event overrides from the event overrides directory."""
        template = "event_override.py"
        overrides: dict[str, dict[str, EventOverride]] = {}
        # Iterate over every event override in every folder
        for folder in os.listdir(EVENT_OVERRIDES):
            if folder == template:
                continue
            # Get the event override ID
            override_id = re.match(r"\d+", folder)
            if not override_id:
                raise ValueError(
                    f"Event override folder `{folder}` does not have an ID!"
                )
            override_id = override_id.group()
            overrides[override_id] = {}
            events = overrides[override_id]
            for event in os.listdir(f"{EVENT_OVERRIDES}/{folder}/"):
                if not event.endswith(".py"):
                    continue
                name = event[:-3]
                module_name = f"source.event_overrides.{folder}.{name}"
                module = importlib.import_module(module_name)
                events[module.event.name] = getattr(module, name)()
        self.event_overrides = overrides
