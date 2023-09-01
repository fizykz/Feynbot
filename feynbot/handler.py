"""Command & Event handler for Feynbot.  `discord.py` listens for events and
calls the respective function here.  In addition it pulls event and command
data from the other directories in this package."""

# Load Folder -> Load Module -> Register -> Listen

from optparse import Option
import os
import pathlib
import importlib
from types import ModuleType
from typing import Callable, Optional
import discord


from feynbot.events import EventTree, get_event_trees
from feynbot.utility import import_from_path
from feynbot.constants import events_list


class Handler:
    """Command & Event handler for Feynbot."""

    def __init__(
        self,
        bot,
        events_directory: str,
        commands_directory: str,
        *args,
        **kwargs,
    ) -> None:
        self.events_directory = events_directory
        self.commands_directory = commands_directory
        self.bot = bot
        self.console = bot.console
        self.event_trees: EventTree = EventTree("MainTree", inherit=False)
        self.command_trees: dict[str, EventTree] = {}

        self.load_and_register_all()

        def get_handler(self, event_name) -> Callable:
            async def handler(*args, **kwargs) -> None:
                await self.fire_event(event_name, *args, **kwargs)

            handler.__name__ = event_name + "_handler"
            return handler

        for event in events_list:
            # TODO: Throw error if an event is enabled but the intent is not.
            setattr(self, event, get_handler(self, event))

        super().__init__(*args, **kwargs)

    async def fire_event(self, event_name: str, *args, **kwargs) -> None:
        # TODO: Impement checking, permissions, overrides
        # TODO: Construct context, pass to event, etc.

        await self.event_trees(
            event_name, *args, context=None, bot=self.bot, db=None, **kwargs
        )

    # def reload(self) -> None:
    #     # TODO: Implement with reload command from importlib

    def load_and_register_all(self) -> None:
        event_trees = self.load_event_trees()
        for tree in event_trees:
            tree.parent_to(self.event_trees)
        # commands = self.load_commands()
        # self.register_commands(commands)

    def load_event_trees(self) -> tuple[EventTree]:
        all_trees = []
        for path in pathlib.Path(self.events_directory).rglob("*.py"):
            if not path.is_file():
                continue
            module = import_from_path(str(path))
            trees = get_event_trees(module)
            if len(trees) == 0:
                self.bot.warn(f"Module `{module}` has no event trees.")
                continue
            all_trees += trees
        return tuple(all_trees)
