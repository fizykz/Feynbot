"""The command and command tree classes."""

import discord
import discord.app_commands as commands


class CommandTree(commands.CommandTree):
    """A command tree for Feynbot."""

    def __init__(self, bot: discord.Client, *args, **kwargs) -> None:
        """Initialize the command tree."""
        super().__init__(bot, *args, **kwargs)


class Command(commands.Command):
    """A command for Feynbot."""

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the command."""
        super().__init__(*args, **kwargs)
