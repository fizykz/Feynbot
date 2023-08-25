"""Contains the Feynbot class and relevant high-level methods."""

import discord
import os
from rich.console import Console
from rich.traceback import install

# Setup
install()


class Feynbot(discord.Client):
    """The Feynbot class, extending `discord.Client`."""

    def __init__(self, token_public: str, token: str, *args, **kwargs) -> None:
        """Initialize the bot."""
        # Arguments & KW Arguments
        self.token_public = token_public
        self.token = token
        self.references = kwargs.get("references", {})
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

        # Event Declaration
        self.event(self.on_ready)

        # Pass to super
        super().__init__(*args, **kwargs)

    # Methods
    def print(self, *args, **kwargs):
        """Print to the console."""
        self.console.print(*args, **kwargs)

    # Overrides
    def run(self, *args, reconnect: bool = True, **kwargs) -> None:
        """Start the bot."""
        super().run(self.token, reconnect=reconnect, *args, **kwargs)

    # Events
    async def on_ready(self) -> None:
        """Print a message when the bot is ready."""
        self.console.print("[bold green]Feynbot is ready![/bold green]")
