"""Contains the Feynbot class and relevant high-level methods."""

import os
import discord
from rich.console import Console
from rich.traceback import install

from source.handler_bot import HandlerBot

# Setup
install()


class Feynbot(HandlerBot, discord.Client):
    """The Feynbot class, extending `discord.Client`."""

    def __init__(self, token: str, *args, **kwargs) -> None:
        """Initialize the bot."""
        # Arguments & KW Arguments
        self.name = kwargs.pop("name", "Feynbot")
        self.token_public = kwargs.pop("token_public", None)
        self.token_app = kwargs.pop("token_app", None)
        self.references = kwargs.pop("references", {})
        self.prefix = kwargs.pop("prefix", ">")
        self.token = token
        self.ready = False
        # TODO: Ensure that bot.ready = False when the bot crashes/etc.
        # TODO: Ignore/delay events until bot.ready = True
        kwargs["max_messages"] = kwargs.get("max_messages", 1000)
        kwargs["intents"] = kwargs.get("intents", {})
        kwargs["status"] = kwargs.get("status", None)
        kwargs["activity"] = kwargs.get("activity", None)
        kwargs["allowed_mentions"] = kwargs.get(
            "allowed_mentions",
            discord.AllowedMentions(
                users=True,
                replied_user=True,
            ),
        )

        # Set Up
        self.console = Console()
        os.system("cls" if os.name == "nt" else "clear")
        self.print("[bold green]Feynbot is starting...[/bold green]")
        kwargs["intents"] = discord.Intents(**kwargs["intents"])

        # Pass to super
        super().__init__(self, *args, **kwargs)

    # Methods
    def print(self, *args, **kwargs):
        """Print to the console."""
        self.console.print(*args, **kwargs)

    # Overrides
    def run(self, *args, reconnect: bool = True, **kwargs) -> None:
        """Start the bot."""
        super().run(self.token, reconnect=reconnect, *args, **kwargs)
