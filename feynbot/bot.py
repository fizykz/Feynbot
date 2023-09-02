"""Contains the Feynbot class and relevant high-level methods."""

# System
import os
import inspect

# Application
import discord
from numpy import stack
from rich.console import Console
from rich.traceback import install

# Local
from Feynbot.handler import Handler

# Setup
install()


class Feynbot(discord.Client, Handler):
    def __init__(self, token: str, **kwargs) -> None:
        # Arguments & KW Arguments
        self.name = kwargs.pop("name", "Feynbot")
        self.token_public = kwargs.pop("token_public", None)
        self.token_app = kwargs.pop("token_app", None)
        self.references = kwargs.pop("references", {})
        self.prefix = kwargs.pop("prefix", ">")
        self.events_directory: str = kwargs.pop("events_directory")
        self.commands_directory: str = kwargs.pop("commands_directory")
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

        # Set Up Console
        self.console = Console()
        os.system("cls" if os.name == "nt" else "clear")
        self.print = self.console.print
        self.log = self.console.log
        self.print("[bold green]Feynbot is starting...[/bold green]")

        # Pass to super
        kwargs["intents"] = discord.Intents(**kwargs["intents"])
        discord.Client.__init__(self, **kwargs)
        Handler.__init__(self, self, self.events_directory, self.commands_directory)

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
    def error(self, message: str, stack_offset: int = 2):
        self.log(f"[bold red]ERROR: {message}[/bold red]", _stack_offset=stack_offset)

    def warning(self, message: str, stack_offset: int = 2):
        self.log(
            f"[bold orange]WARNING: {message}[/bold orange]", _stack_offset=stack_offset
        )

    # Methods
    def to_ids(self, *args) -> list[int]:
        return [arg.id for arg in args]

    # Overrides
    def run(self, *args, reconnect: bool = True, **kwargs) -> None:
        super().run(
            self.token,
            reconnect=reconnect,
            *args,
            log_handler=kwargs.get("log_handler", None),
            **kwargs,
        )
