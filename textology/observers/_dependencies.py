"""Dependencies for input/output requests via observation callbacks."""

from typing import Any
from typing import Iterable
from typing import Protocol

CALLBACK_EXCEPTION_ID = "_callback_exception_id"


class SupportsID(Protocol):
    """Type class to indicate an object that has an "id" attribute."""

    id: str


class Dependency:
    """Base for all observation dependencies."""

    def __init__(
        self,
        component_id: str | SupportsID,
        component_property: str,
    ) -> None:
        """Initialize base dependency identification.

        Args:
            component_id: ID, or object with ID property, that a component uses to send and receive updates.
            component_property: Property name on the component that sends and receives updates.
        """
        self.component_id = component_id if isinstance(component_id, str) else component_id.id
        self.component_property = component_property

    def __eq__(self, other: Any) -> bool:
        """Evaluate if another object is equal to this Dependency."""
        return (
            isinstance(other, Dependency)
            and self.component_id == other.component_id
            and self.component_property == other.component_property
        )

    def __hash__(self) -> int:
        """Convert object into hash usable in maps."""
        return hash(str(self))

    def __repr__(self) -> str:
        """Convert object into human-readable, machine loadable, text."""
        return f"{self.__class__.__name__}('{self.component_id}', '{self.component_property}')"


class Modified(Dependency):
    """Triggering input of an observation callback based on a stateful attribute update.

    Property/attribute to monitor for modifications and trigger observation callbacks.
    """


class NoUpdate:
    """Empty type that indicates that a specific update should be ignored in an observation callback."""


no_update = NoUpdate()


class Published(Dependency):
    """Triggering input of an observation callback based on a stateless event, rather than a stateful property.

    Event type to monitor for announcements and trigger observation callbacks.
    """

    def __init__(
        self,
        component_id: str | SupportsID,
        component_event: type,
    ) -> None:
        """Initialize published event dependency.

        Args:
            component_id: ID, or object with ID property, that a component uses to send updates.
            component_event: Event type that is sent from the component to trigger updates.
        """
        super().__init__(
            component_id if isinstance(component_id, str) else component_id.id,
            f"{component_event.__module__}.{component_event.__name__}",
        )
        self.component_event = component_event


class Raised(Dependency):
    """Triggering input of an observation callback based on an exception being raised during another callback.

    Special dependency type that is called when exceptions are raised during invocation of other callbacks.
    Exception handler callbacks are only invoked if an exception occurs during another callback,
    not if an exception happens during collection or application of the callback. Observation managers/applications
    are responsible for handling exceptions during collection/application phases before/after the callback.
    """

    def __init__(
        self,
        exception_type: type[BaseException],
    ) -> None:
        """Initialize raised exception dependency.

        Args:
            exception_type: Exception type that is caught from callbacks.
        """
        super().__init__(
            CALLBACK_EXCEPTION_ID,
            f"{exception_type.__module__}.{exception_type.__name__}",
        )
        self.exception_type = exception_type


class Select(Dependency):
    """Non-triggering input of an observation callback.

    Most recent property value to send to a callback without triggering if the property is updated.
    """


class Update(Dependency):
    """Output of an observation callback that will update another component.

    Property to apply after an input triggers an observation callback.
    """


DependencyType = Modified | Published | Raised | Select | Update


def flatten_dependencies(
    args: Iterable,
) -> dict[type[Dependency], list[Dependency]]:
    """Split arguments into organized dependency groups based on their types.

    Args:
        args: Positional arguments containing one or more Dependencies.

    Returns:
        Flat lists of combined dependencies, pulled from arguments regardless of order.
    """
    types: dict[type[Dependency], list] = {
        Published: [],
        Modified: [],
        Raised: [],
        Select: [],
        Update: [],
    }
    for arg in args:
        if not isinstance(arg, Dependency):
            continue
        types[arg.__class__].append(arg)
    return types


def validate_dependencies(*dependencies: Dependency) -> None:
    """Check all the dependencies to ensure they create a valid callback.

    Args:
        dependencies: All dependencies used by an observer/callback.

    Raises:
        ValueError if missing any requirements or any combination is invalid, such as duplicates.
    """
    triggers = []
    trigger_props = {}
    raises = []
    for dependency in dependencies:
        component_id = dependency.component_id
        component_property = dependency.component_property
        if isinstance(dependency, Raised):
            raises.append(dependency)
        if raises and isinstance(dependency, (Modified, Published)):
            raise ValueError("No other triggering input dependencies are allowed with exception handlers, only Selects")
        if isinstance(dependency, (Modified, Published, Raised)):
            trigger_props.setdefault(component_id, set())
            if component_id != CALLBACK_EXCEPTION_ID and component_property in trigger_props[component_id]:
                raise ValueError(f"Duplicate trigger dependency found for {component_id}:{component_property}")
            triggers.append(dependency)
            trigger_props[component_id].add(component_property)
    if not triggers:
        raise ValueError("No trigger dependency found")
