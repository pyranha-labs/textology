"""Dependencies for input/output requests via observation callbacks."""

from typing import Any
from typing import Protocol


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
    """Triggering input of an observation callback.

    Property to monitor for modifications and trigger observation callbacks.
    """


class NoUpdate:
    """Empty type that indicates that a specific update should be ignored in an observation callback."""


class Select(Dependency):
    """Non-triggering input of an observation callback.

    Most recent property value to send to a callback without triggering if the property is updated.
    """


class Update(Dependency):
    """Output of an observation callback that will update another component.

    Property to apply after a modification triggers an observation callback.
    """


def flatten_dependencies(
    args: tuple,
) -> tuple[list[Modified], list[Select], list[Update]]:
    """Split arguments into modifications (triggering inputs), selections (non-triggering inputs), and updates.

    Args:
        args: Positional arguments containing one or more Dependencies.

    Returns:
        Flat lists of combined modification(s), select(s), and update(s), pulled from arguments regardless of order.
    """
    updates = []
    modifications = []
    selections = []
    for arg in args:
        if isinstance(arg, Update):
            updates.append(arg)
        elif isinstance(arg, Modified):
            modifications.append(arg)
        elif isinstance(arg, Select):
            selections.append(arg)
    return modifications, selections, updates
