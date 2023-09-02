"""Command & Event handler for Feynbot.  `discord.py` listens for events and
calls the respective function here.  In addition it pulls event and command
data from the other directories in this package."""

# Load Folder -> Load Module -> Register -> Listen

import pathlib
import importlib
from typing import Callable, Optional
from discord import Interaction
from discord import Object as DObject

import discord.app_commands as app_commands
from discord.app_commands import Command as DCommand

from Feynbot.commands import CommandTree, get_command_trees
from Feynbot.events import EventTree, get_event_trees
from Feynbot.utility import import_from_path
from Feynbot.constants import events_list


class Handler:
    """Command & Event handler for Feynbot."""

    def __init__(
        self,
        bot,
        events_directory: str,
        commands_directory: str,
    ) -> None:
        self.events_directory = events_directory
        self.commands_directory = commands_directory
        self.bot = bot
        self.console = bot.console
        self.event_trees: EventTree = EventTree("Root")
        self.command_trees: CommandTree = CommandTree("Root")
        self.dcommand_tree: app_commands.CommandTree = app_commands.CommandTree(
            bot,
            fallback_to_global=False,
        )

        self.load_and_register_all()
        self.hook_events()
        self.hook_commands()

    # General Methods
    def load_and_register_all(self) -> None:
        event_trees = self.load_event_trees()
        for tree in event_trees:
            tree.parent_to(self.event_trees, inherit=False)
        command_trees = self.load_command_trees()
        for tree in command_trees:
            tree.parent_to(self.command_trees, inherit=False)

    def reload_all(self) -> None:
        self.reload_events()
        self.reload_commands()

    def reload_events(self) -> None:
        pass

    def reload_commands(self) -> None:
        pass

    # Event Methods
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

    def hook_events(self) -> None:
        def hook(self, event_name) -> Callable:
            async def handler(*args, **kwargs) -> None:
                await self.fire_event(event_name, *args, **kwargs)

            handler.__name__ = event_name + "_event_hook"
            return handler

        for event in events_list:
            # TODO: Throw error if an event is enabled but the intent is not.
            setattr(self, event, hook(self, event))
        return

    async def fire_event(self, event_name: str, *args, **kwargs) -> None:
        # TODO: Impement checking, permissions, overrides
        # TODO: Construct context, pass to event, etc.
        raw = {
            "args": args,
            **kwargs,
        }
        kwargs = {
            "context": None,
            "bot": self.bot,
            "db": None,
            "raw": raw,
        }
        await self.event_trees(event_name, **kwargs)
        return

    # Command Methods
    def load_command_trees(self) -> tuple[CommandTree]:
        all_trees = []
        for path in pathlib.Path(self.commands_directory).rglob("*.py"):
            module = import_from_path(str(path))
            trees = get_command_trees(module)
            if len(trees) == 0:
                self.bot.warn(f"Module `{module}` has no command trees.")
                continue
            all_trees += trees
        return tuple(all_trees)

    def hook_commands(self) -> None:
        def hook(self, command_name) -> Callable:
            async def handler(interaction: Interaction) -> None:
                # NOTE: Will need to pass Interaction or make a Context
                self.log(f"Command `{command_name}` fired.")
                await self.fire_command(command_name)

            handler.__name__ = command_name + "_command_hook"
            return handler

        print(repr(self.command_trees))
        for command in self.command_trees:
            # FIX: Currently, there are subtle errors, such as when description
            # is an empty string.  These need to raise an exception.
            if command.initialized() is False:
                raise ValueError(f"Command `{command.name}` is not initialized.")
            self.dcommand_tree.command(
                name=command.command_name,
                description=command.description,
                guilds=command.get_gid_snowflakes(),
            )(hook(self, command.name))
        return

    async def sync_commands(self, *guilds: Optional[DObject]) -> None:
        if len(guilds) == 0:
            await self.dcommand_tree.sync()
            return
        for guild in guilds:
            await self.dcommand_tree.sync(guild=guild)
        return

    async def fire_command(self, command_name: str, *args, **kwargs) -> None:
        # TODO: Impement checking, permissions, overrides
        # TODO: Construct context, pass to event, etc.
        raw = {
            "args": args,
            **kwargs,
        }
        kwargs = {
            "context": None,
            "bot": self.bot,
            "db": None,
            "raw": raw,
        }
        await self.command_trees(command_name, **kwargs)
        return
