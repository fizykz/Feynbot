from asyncio import iscoroutinefunction
from types import ModuleType
from typing import Any, Awaitable, Callable, Optional
from inspect import currentframe

from anytree import NodeMixin, RenderTree

from Feynbot.constants import events_list
from Feynbot.utility import check_kwargs

silenced_events = []


class EventTree(NodeMixin):
    def __init__(
        self,
        node_name: Optional[str] = None,
        enabled: Optional[bool] = None,
        persistent: Optional[bool] = None,
        terminal: Optional[bool] = None,
        priority: Optional[int] = None,
        oid: Optional[int] = None,
        oids: Optional[list[int]] = None,
        **kwargs: Any,
    ) -> None:
        # Pre-initialization
        self.events: dict[str, list[Event]] = {}
        self.enabled: bool = True
        self.persistent: bool = False
        self.terminal: bool = False
        self.priority: int = 0
        self.oids: list[int] = list()  # CHANGE: `oids` can be made `set[int]`
        # Construct subobject
        super().__init__()
        # Check for a parent and inherit
        parent = kwargs.pop("parent", None)
        if parent:
            self.parent_to(parent, inherit=True)
        # Get file info from where this was defined
        caller_variables = currentframe().f_back.f_globals  # type: ignore
        self.origin = kwargs.pop("origin", caller_variables["__name__"])
        self.file_path = kwargs.pop("file_path", caller_variables["__file__"])
        # Set (default) attributes
        self.name: str = node_name or self.origin
        self.signature: str = self.name
        # self.signature: str = self.name + f" [{self.file_path}]" # Extra info
        self.enabled: bool = enabled or self.enabled
        self.persistent: bool = persistent or self.persistent
        self.terminal: bool = terminal or self.terminal
        self.priority: int = priority or self.priority

        self.is_global: bool = True
        if oids and oid:
            raise ValueError("Cannot have both `oid` and `oids`.")
        if oid:
            self.set_oids(oid)
        elif oids:
            self.set_oids(*oids)
        check_kwargs(kwargs)

    # OID Methods
    def set_oids(self, *oids: int) -> None:
        self.oids = list(oids)
        self.is_global = len(self.oids) == 0

    def add_oids(self, *oids: int) -> None:
        self.oids.extend([oid for oid in oids if oid not in self.oids])
        self.is_global = len(self.oids) == 0

    def remove_oids(self, *oids: int) -> None:
        self.oids = [oid for oid in self.oids if oid not in oids]
        self.is_global = len(self.oids) == 0

    def bind(
        self,
        event_name: str,
        node_name: Optional[str] = None,
        oid: Optional[int] = None,
        oids: Optional[list[int]] = None,
        **kwargs: Any,
    ) -> Callable[[Callable], Any]:
        # Get file info from where this was defined
        caller_variables = currentframe().f_back.f_globals  # type: ignore
        origin = kwargs.pop("origin", caller_variables["__name__"])
        file_path = kwargs.pop("file_path", caller_variables["__file__"])

        event = Event(
            node_name=node_name,
            oid=oid,
            oids=oids,
            origin=kwargs.get("origin", origin),
            file_path=kwargs.get("file_path", file_path),
            parent=self,
            **kwargs,
        )
        decorator = event.bind(event_name)
        return decorator

    def parent_to(self, parent: "EventTree", inherit: bool = True) -> None:
        self.parent = parent
        if inherit:
            self.inherit_from(parent)
        for events in self.events.values():
            for event in events:
                parent.register_event(event)

    def adopt_tree(self, child: "EventTree", inherit: bool = True) -> None:
        child.parent_to(self, inherit=inherit)

    def register_event(self, event: "Event", recursive: bool = True) -> None:
        event_name = event.event_name
        if event_name is None:
            raise ValueError("Event must have an event_name.")
        if event_name not in self.events:
            self.events[event_name] = list()
        self.events[event_name].append(event)
        self.sort(event_name)
        if self.parent and recursive:
            self.parent.register_event(event)

    def inherit_from(self, node: "EventTree") -> None:
        self.enabled = node.enabled
        self.persistent = node.persistent
        self.terminal = node.terminal
        self.priority = node.priority
        self.set_oids(*node.oids)

    def has(self, event_name: str) -> bool:
        return event_name in self.events

    def sort(self, event_name: Optional[str]) -> None:
        if event_name is None:
            for event_name in self.events:
                self.sort(event_name)
            return

        def sort_key(event_object: Event) -> int:
            return -event_object.priority

        self.events[event_name].sort(key=sort_key)

    async def fire(self, event_name: str, *args: Any, **kwargs: Any) -> Any:
        # Not silenced and not found:
        if event_name not in silenced_events and not self.has(event_name):
            silenced_events.append(event_name)
            raise IndexError(
                f"Event `{event_name}` not found in `{self.signature}`.  This event "
                f"will now be silenced."
            )
        # Silenced and not found:
        elif not self.has(event_name):
            return
        # Found:
        terminal_flag = False
        # Run events in order (presorted by priority)
        for event in self.events[event_name]:
            # Terminal and not persistent:
            if terminal_flag and not event.persistent:
                continue
            # Not terminal or persistent:
            await event(*args, **kwargs)
            if event.terminal:
                terminal_flag = True

    def __call__(self, event, *args: Any, **kwargs: Any) -> Any:
        """Call the event."""
        return self.fire(event, *args, **kwargs)

    def __str__(self) -> str:
        string = f"{self.name}"
        node = self.parent
        while node:
            string = f"{node.name}.{string}"
            node = node.parent
        return string

    def __repr__(self) -> str:
        return RenderTree(self).by_attr("signature")


class Event(EventTree):
    def __init__(
        self,
        node_name: Optional[str] = None,
        enabled: Optional[bool] = None,
        persistent: Optional[bool] = None,
        terminal: Optional[bool] = None,
        priority: Optional[int] = None,
        oid: Optional[int] = None,
        oids: Optional[list[int]] = None,
        **kwargs: Any,
    ) -> None:
        # Get file info from where this was defined
        caller_variables = currentframe().f_back.f_globals  # type: ignore
        origin = kwargs.pop("origin", caller_variables["__name__"])
        file_path = kwargs.pop("file_path", caller_variables["__file__"])
        # Construct node
        super().__init__(
            node_name=node_name,
            enabled=enabled,
            persistent=persistent,
            terminal=terminal,
            priority=priority,
            oid=oid,
            oids=oids,
            origin=kwargs.get("origin", origin),
            file_path=kwargs.get("file_path", file_path),
            **kwargs,
        )
        # Set attributes
        self.signature = self.signature + " @"
        self.event_name: Optional[str] = None
        self.function: Optional[Callable[..., Optional[Awaitable[None]]]] = None
        self.is_coroutine: bool

    def bind(
        self,
        event_name: str,
        node_name: Optional[str] = None,
        oid: Optional[int] = None,
        oids: Optional[list[int]] = None,
        **kwargs: Any,  # IMPLEMENT: Overriding attributes/erroring if overriding
    ) -> Callable[[Callable[..., Optional[Awaitable[None]]]], Any]:
        if event_name not in events_list:
            raise ValueError(f"`{event_name}` is not a valid event.")
        if self.event_name is not None:
            raise ValueError(
                f"Event `{self.event_name}` already bound for this "
                f"listener from `{self.origin}`."
            )

        def decorator(function: Callable[..., Optional[Awaitable[None]]]) -> None:
            self.function = function
            if node_name and self.name != node_name:
                raise ValueError(
                    f"Tried passing `node_name = {node_name}` while binding when "
                    f"`self.name = {self.name}` was already defined in {self}.  "
                    f"Consider removing one of the two or renaming the function "
                    f"after binding."
                )
            self.name = node_name or self.name or function.__name__
            self.is_coroutine = iscoroutinefunction(function)

        self.event_name = event_name
        self.signature = self.signature + f"{self.priority} " + self.event_name
        self.register_event(self)
        return decorator

    def has(self, event_name: str) -> bool:
        return self.event_name == event_name

    async def fire(self, *args: Any, **kwargs: Any) -> None:
        # FIX: Currently, this will only fire the first event in the hierarchy.
        # of the same `event_name` as this overrides the `fire` method of `EventTree`
        if not self.enabled:
            return
        if not callable(self.function):
            raise IndexError(
                f"Event {self.event_name} from file {self.origin} not bound "
                f"to any valid function but was called."
            )
        if iscoroutinefunction(self.function):
            await self.function(*args, **kwargs)
        else:
            self.function(*args, **kwargs)

    def __call__(self, *args: Any, **kwargs: Any) -> Awaitable[None]:
        # CHANGE:  This can probably be removed to use the method from `EventTree`,
        # but it may cause issues.
        return self.fire(*args, **kwargs)


def get_event_trees(module: ModuleType, roots_only: bool = True) -> tuple[EventTree]:
    variables = dir(module)
    event_containers = []
    if "_no_import" in variables:
        return tuple()
    for variable in variables:
        if variable.startswith("__"):
            continue
        value = getattr(module, variable)
        if isinstance(value, EventTree) and value.parent is None:
            if roots_only and value.parent is not None:
                continue
            event_containers.append(value)
    return tuple(event_containers)
