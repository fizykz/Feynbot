"""The command and command tree classes."""

from asyncio import iscoroutinefunction
from types import ModuleType
from typing import Any, Awaitable, Callable, Collection, Iterator, Optional
from inspect import currentframe

from discord import Object as DObject
from discord.app_commands import Command as DCommand
from anytree import NodeMixin, RenderTree

from Feynbot.utility import check_kwargs

# IMPLEMENT: handling parameters, autocomplete, syncing, etc.


class CommandTree(NodeMixin):
    def __init__(
        self,
        node_name: Optional[str] = None,
        enabled: bool = True,
        gid: Optional[int] = None,
        gids: Optional[list[int]] = None,
        **kwargs: Any,
    ) -> None:
        # Pre-Initialization
        self.override_commands: dict[str, dict[int, Command]] = {}
        self.global_commands: dict[str, Command] = {}
        # Construct node
        super().__init__()
        # Check for parent
        parent = kwargs.pop("parent", None)
        if parent:
            self.parent_to(parent, inherit=True)
        # Get file info from where this was defined
        caller_variables = currentframe().f_back.f_globals  # type: ignore
        self.origin = kwargs.pop("origin", caller_variables["__name__"])
        self.file_path = kwargs.pop("file_path", caller_variables["__file__"])
        # Set attributes
        self.name = node_name or self.origin
        self.signature = self.name
        self.enabled = enabled

        self.gids: list[int] = list()
        self.is_global: bool = True
        if gids and gid:
            raise ValueError("Cannot have both `gid` and `gids`.")
        if gid:
            self.set_gids(gid)
        elif gids:
            self.set_gids(*gids)
        check_kwargs(kwargs)

    # GID Methods
    # FIX: All of these methods have the potential to break the tree structure since
    # they don't update whether they store the command globally or as an override.
    def set_gids(self, *gids: int) -> None:
        self.gids = list(gids)
        self.is_global = len(self.gids) == 0

    def add_gids(self, *gids: int) -> None:
        self.gids.extend([gid for gid in gids if gid not in self.gids])
        self.is_global = len(self.gids) == 0

    def remove_gids(self, *gids: int) -> None:
        self.gids = [gid for gid in self.gids if gid not in gids]
        self.is_global = len(self.gids) == 0

    def get_gid_snowflakes(self) -> tuple[DObject]:
        snowflakes = []
        for gid in self.gids:
            snowflakes.append(DObject(id=gid))
        return tuple(snowflakes)

    # Logic Methods
    def has(
        self,
        command_name: str,
        *_,
        is_global: Optional[bool] = None,
        gid: Optional[int] = None,
    ) -> bool:
        if is_global is None:
            return self.has(command_name, True) or self.has(command_name, False)
        if is_global:
            return command_name in self.global_commands
        if command_name in self.override_commands:
            command_set = self.override_commands[command_name]
            if gid is not None:
                return gid in command_set
            return len(command_set) > 0
        return False

    def parent_to(self, parent: "CommandTree", inherit: bool = True) -> None:
        self.parent = parent
        if inherit:
            self.inherit_from(parent)
        for command in self.global_commands.values():
            parent.register_command(command)
        for command_set in self.override_commands.values():
            for command in command_set.values():
                parent.register_command(command)

    def inherit_from(self, node: "CommandTree") -> None:
        self.enabled = node.enabled
        self.set_gids(*node.gids)

    def adopt_tree(self, child: "CommandTree", inherit: bool = True) -> None:
        child.parent_to(self, inherit=inherit)

    # Command Methods
    def bind(
        self,
        command_name: str,
        node_name: Optional[str] = None,
        enabled: bool = True,
        gid: Optional[int] = None,
        gids: Optional[list[int]] = None,
        **kwargs: Any,
    ) -> Callable[[Callable], None]:
        # Get file info from where this was defined
        caller_variables = currentframe().f_back.f_globals  # type: ignore
        origin = kwargs.pop("origin", caller_variables["__name__"])
        file_path = kwargs.pop("file_path", caller_variables["__file__"])

        command = Command(
            command_name=command_name,
            node_name=node_name,
            enabled=enabled,
            gid=gid,
            gids=gids,
            origin=kwargs.get("origin", origin),
            file_path=kwargs.get("file_path", file_path),
            parent=self,
            **kwargs,
        )
        decorator = command.bind(command_name)
        return decorator

    def register_command(self, command: "Command", recursive: bool = True) -> None:
        command_name = command.name
        if command_name is None:
            raise ValueError(f"Command `{command}` has no name.")
        # Global command:
        if command.is_global:
            self.global_commands[command_name] = command
        # Override command:
        if command_name not in self.override_commands:
            self.override_commands[command_name] = {}
        command_set = self.override_commands[command_name]
        for gid in command.gids:
            # If preexisting:
            if gid in command_set and command_set[gid] != command:
                raise ValueError(
                    f"Command `{command}` conflicts with `{command_set[gid]}`."
                )
            command_set[gid] = command
        if self.parent and recursive:
            self.parent.register_command(command)

    async def fire(self, name: str, *args, **kwargs) -> None:
        # IMPLEMENT:  Overrides need to be specially handled here.
        pass

    # Special Methods
    def __call__(self, name: str, *args, **kwargs) -> Awaitable[None]:
        return self.fire(name, *args, **kwargs)

    def __iter__(self) -> Iterator["Command"]:
        global_commands: Collection[Command] = self.global_commands.values()
        override_commands: list[Command] = []
        for command_set in self.override_commands.values():
            override_commands += command_set.values()
        all_commands: tuple[Command] = tuple(global_commands) + tuple(override_commands)
        return iter(all_commands)

    def __str__(self) -> str:
        string = f"{self.name}"
        node = self.parent
        while node:
            string = f"{node.name}.{string}"
            node = node.parent
        return string

    def __repr__(self) -> str:
        return RenderTree(self).by_attr("signature")


class Command(CommandTree):
    def __init__(
        self,
        command_name: Optional[str] = None,
        node_name: Optional[str] = None,
        enabled: bool = True,
        gid: Optional[int] = None,
        gids: Optional[list[int]] = None,  # CHANGE: This can be made `set[int]`
        **kwargs: Any,
    ) -> None:
        # Pre-Initialization
        self.description: str = kwargs.pop("description", "(No description)")
        # Get file info from where this was defined
        caller_variables = currentframe().f_back.f_globals  # type: ignore
        origin = kwargs.pop("origin", caller_variables["__name__"])
        file_path = kwargs.pop("file_path", caller_variables["__file__"])
        # Construct node
        super().__init__(
            node_name=node_name,
            enabled=enabled,
            gid=gid,
            gids=gids,
            origin=kwargs.get("origin", origin),
            file_path=kwargs.get("file_path", file_path),
            **kwargs,
        )
        # Set attributes
        self.node_name: Optional[str] = node_name
        self.signature = self.signature + " $ "
        self.command_name: Optional[str] = command_name
        self.function: Optional[Callable[..., Optional[Awaitable[None]]]] = None
        self.is_coroutine: bool
        self.discord_command: Optional[DCommand] = None

    def bind(
        self,
        command_name: str,
        node_name: Optional[str] = None,
        enabled: bool = True,
        gid: Optional[int] = None,
        gids: Optional[list[int]] = None,
        **kwargs: Any,  # IMPLEMENT: Overriding attributes/erroring if overriding
    ) -> Callable[[Callable], None]:
        # NOTE:  Currently, `file_path` and `origin` are defined by where
        # the `Command` object itself is defined, not where the bound function is.
        # This needs to be considered.
        if self.function:
            raise ValueError(
                f"Command `{self.command_name}` already bound for this "
                f"listener from `{self.origin}`."
            )

        def decorator(function: Callable[..., Optional[Awaitable[None]]]) -> None:
            self.function = function
            if node_name and self.name and self.name != node_name:
                raise ValueError(
                    f"Tried passing `node_name = {node_name}` while binding when "
                    f"`self.name = {self.name}` was already defined in {self}.  "
                    f"Consider removing one of the two or renaming the function "
                    f"after binding."
                )
            if node_name is None and self.name is None:
                raise ValueError(
                    f"Command `{command_name}` from file {self.origin} has no name."
                )
            self.name = self.name or node_name
            self.is_coroutine = iscoroutinefunction(function)

        self.description = kwargs.get("description", self.description)
        self.command_name = command_name
        self.signature = self.signature + self.command_name
        self.register_command(self)
        return decorator

    def initialized(self) -> bool:
        if self.function is None:
            return False
        if self.command_name is None:
            return False
        return True

    async def fire(self, *args, **kwargs) -> None:
        if not self.enabled:
            return
        if not callable(self.function):
            raise IndexError(
                f"Command {self.command_name} from file {self.origin} not bound "
                f"to any valid function but was called."
            )
        if iscoroutinefunction(self.function):
            await self.function(*args, **kwargs)
        else:
            self.function(*args, **kwargs)

    def __call__(self, *args: Any, **kwds: Any) -> Awaitable[None]:
        return self.fire(*args, **kwds)


def get_command_trees(
    module: ModuleType, roots_only: bool = True
) -> tuple[CommandTree]:
    variables = dir(module)
    command_trees = []
    if "_no_import" in variables:
        return tuple()
    for variable in variables:
        if variable.startswith("__"):
            continue
        value = getattr(module, variable)
        if isinstance(value, CommandTree) and value.parent is None:
            if roots_only and value.parent is not None:
                continue
            command_trees.append(value)
    return tuple(command_trees)
