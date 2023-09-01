"""Contains the Feynbot class and relevant high-level methods."""

# System
import os
import inspect

# Application
import discord
from rich.console import Console
from rich.traceback import install

# Local
from feynbot.handler import Handler

# Setup
install()


class Feynbot(Handler, discord.Client):
    def __init__(self, token: str, *args, **kwargs) -> None:
        # Arguments & KW Arguments
        self.name = kwargs.pop("name", "Feynbot")
        self.token_public = kwargs.pop("token_public", None)
        self.token_app = kwargs.pop("token_app", None)
        self.references = kwargs.pop("references", {})
        self.prefix = kwargs.pop("prefix", ">")
        self.events_directory = kwargs.get("events_directory")
        self.commands_directory = kwargs.get("commands_directory")
        self.token = token
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

    # Async Methods
    def addTask(self, coro) -> None:
        self.loop.create_task(coro)

    def call(self, function, *args, **kwargs):
        if inspect.iscoroutinefunction(function):
            return self.addTask(function(*args, **kwargs))
        return function(*args, **kwargs)

    async def process(self, function, *args, **kwargs) -> None:
        if inspect.iscoroutinefunction(function):
            return await function(*args, **kwargs)
        return function(*args, **kwargs)

    # Logging
    def print(self, *args, **kwargs):
        self.console.print(*args, **kwargs)

    def log(self, *args, **kwargs):
        self.console.log(*args, **kwargs)

    def log_green(self, message: str):
        self.console.print(f"[bold green]{message}[/bold green]")

    def error(self, message: str):
        self.console.print(f"[bold red]ERROR: {message}[/bold red]")

    def warning(self, message: str):
        self.console.print(f"[bold orange]WARNING: {message}[/bold orange]")

    # Methods
    def to_ids(self, *args) -> list[int]:
        return [arg.id for arg in args]

    # Overrides
    def run(self, *args, reconnect: bool = True, **kwargs) -> None:
        super().run(self.token, reconnect=reconnect, *args, **kwargs)
