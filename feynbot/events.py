from asyncio import iscoroutinefunction
from types import ModuleType
from typing import Any, Awaitable, Callable, Optional, Collection
from inspect import currentframe

from anytree import NodeMixin, RenderTree

from feynbot.constants import events_list

silenced_events = []


class EventTree(NodeMixin):
    def __init__(
        self,
        signature: Optional[str] = None,
        enabled: bool = True,
        persistent: bool = False,
        terminal: bool = False,
        priority: int = 0,
        oid: Optional[int] = None,
        oids: Collection[int] = (),
        **kwargs: Any,
    ) -> None:
        # Construct node
        super().__init__()
        # Get file where this was called
        caller = currentframe().f_back.f_globals["__name__"]  # type: ignore
        self.origin = kwargs.pop("origin", caller)
        # Set attributes
        self.signature = signature or self.origin
        self.name = self.signature
        self.enabled = enabled
        self.persistent = persistent
        self.terminal = terminal
        self.priority = priority
        self.events: dict[str, Collection[Event]] = {}
        self.oids: Collection[int] = []
        self.is_global: bool = True
        self.is_local: bool = False
        self.set_oids(oids, oid=oid)

    def set_oids(self, oids: Collection[int], **kwargs) -> None:
        oid = kwargs.pop("oid", None)
        if oid and len(oids) > 0:
            raise ValueError("Cannot have both oid and oids.")
        if oid:
            self.oids = [oid]
        else:
            self.oids = oids
        self.is_global = len(self.oids) == 0
        self.is_local = not self.is_global

    def bind(
        self,
        event: str,
        signature: Optional[str] = None,
        oid: Optional[int] = None,
        oids: Collection[int] = (),
        inherit: bool = True,
        **kwargs: Any,
    ) -> Callable[[Callable], Any]:
        # Get file where this was called
        caller = currentframe().f_back.f_globals["__name__"]  # type: ignore
        self.origin = kwargs.pop("origin", caller)

        event_object = Event(
            signature=signature,
            oid=oid,
            oids=oids,
            origin=kwargs.get("origin", caller),
        )
        event_object.parent_to(self, inherit=inherit)
        decorator = event_object.bind(event)
        return decorator

    def parent_to(self, parent: "EventTree", inherit: bool = True) -> None:
        self.parent = parent
        if inherit:
            self.inherit_from(parent)
        for event, event_objects in self.events.items():
            for event_object in event_objects:
                parent.add_to_events(event, event_object)

    def adopt_tree(self, event_tree: "EventTree", inherit: bool = True) -> None:
        event_tree.parent_to(self, inherit=inherit)

    def add_to_events(
        self, event: str, event_objects: "Event", recursive: bool = True
    ) -> None:
        if event not in self.events:
            self.events[event] = []
        if not hasattr(self.events[event], "append"):
            raise AttributeError(
                f"Event {event} from file {self.origin} does not have an "
                f"append method."
            )
        self.events[event].append(event_objects)  # type:ignore
        self.sort(event)
        if self.parent and recursive:
            self.parent.add_to_events(event, event_objects)

    def inherit_from(self, event_tree: "EventTree") -> None:
        self.enabled = event_tree.enabled
        self.persistent = event_tree.persistent
        self.terminal = event_tree.terminal
        self.priority = event_tree.priority
        self.set_oids(event_tree.oids)

    def has(self, event: str) -> bool:
        return event in self.events

    def sort(self, event) -> None:
        def sort_key(event_object: Event) -> int:
            return -event_object.priority

        if not hasattr(self.events[event], "sort"):
            raise AttributeError(
                f"Event {event} from file {self.origin} does not have a sort "
                f"method."
            )
        self.events[event].sort(key=sort_key)  # type:ignore

    async def fire(self, event: str, *args: Any, **kwargs: Any) -> Any:
        if not self.has(event) and event not in silenced_events:
            silenced_events.append(event)
            raise IndexError(
                f"Event {event} not found in {self.signature}.  This event "
                f"will now be silenced."
            )
        elif not self.has(event):
            return
        flag_terminal = False
        # Run events in order (presorted by priority)
        for event_object in self.events[event]:
            if flag_terminal and not event_object.persistent:
                continue
            await event_object(*args, **kwargs)
            if event_object.terminal:
                flag_terminal = True

        # Create Context
        # Get Database Interface

    def __call__(self, event, *args: Any, **kwargs: Any) -> Any:
        """Call the event."""
        return self.fire(event, *args, **kwargs)

    def __str__(self) -> str:
        return RenderTree(self).by_attr("name")


class Event(EventTree):
    def __init__(
        self,
        signature: Optional[str] = None,
        enabled: bool = True,
        persistent: bool = False,
        terminal: bool = False,
        priority: int = 0,
        oid: Optional[int] = None,
        oids: Collection[int] = (),
        **kwargs: Any,
    ) -> None:
        super().__init__(
            signature=signature,
            enabled=enabled,
            persistent=persistent,
            terminal=terminal,
            priority=priority,
            oid=oid,
            oids=oids,
            origin=kwargs.get("origin", None),
        )
        self.event: Optional[str] = None
        self.function: Optional[Callable[..., Awaitable[None]]] = None
        self.is_coroutine: Optional[bool] = None

    def bind(  # pylint: disable=arguments-differ
        self,
        event: str,
        signature: Optional[str] = None,
        oid: Optional[int] = None,
        oids: Collection[int] = (),
        **kwargs: Any,
    ) -> Callable[[Callable[..., Awaitable[None]]], Any]:
        if event not in events_list:
            raise ValueError(f"`{event}` is not a valid event.")
        if self.event is not None:
            raise IndexError(
                f"Event `{self.event}` already bound for this "
                f"listener from `{self.origin}`."
            )

        self.event = event
        self.name = self.signature + " @ " + self.event
        self.add_to_events(event, self)

        def decorator(function: Callable[..., Awaitable[None]]) -> None:
            self.function = function
            self.signature = signature or function.__name__
            self.is_coroutine = iscoroutinefunction(function)

        return decorator

    def has(self, event: str) -> bool:
        return self.event == event

    async def fire(self, *args: Any, **kwargs: Any) -> None:
        if not self.enabled:
            return
        if not self.function:
            raise IndexError(
                f"Event {self.event} from file {self.origin} not bound "
                f"to any function but was called."
            )
        if iscoroutinefunction(self.function):
            await self.function(*args, **kwargs)
        else:
            self.function(*args, **kwargs)

    def __call__(self, *args: Any, **kwargs: Any) -> Awaitable[None]:
        return self.fire(*args, **kwargs)


def get_event_trees(module: ModuleType) -> tuple[EventTree]:
    """From a module, get all defined `EventTree`.

    Args:
        module (ModuleType): The module to search.

    Returns:
        tuple[EventTree]: Tuple of `EventTree` objects.
    """
    variables = dir(module)
    event_containers = []
    for variable in variables:
        if variable.startswith("__"):
            continue
        value = getattr(module, variable)
        if isinstance(value, EventTree):
            event_containers.append(value)
    return tuple(event_containers)
