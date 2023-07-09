#!/usr/bin/env python3

"""Basic example of set up and loop for an input/output application."""

import asyncio

from textology.observers import Modified
from textology.observers import ObservedObject
from textology.observers import ObservedValue
from textology.observers import ObserverManager
from textology.observers import Select
from textology.observers import Update


class Component(ObservedObject):
    """Basic example of a component object that has observed values."""

    value = ObservedValue(None)

    def __init__(self, id: str = None) -> None:
        """Initialize component with an id for searching."""
        super().__init__()
        self.id = id


class App(ObserverManager):
    """Basic example of an application that listens to changes to components."""

    def __init__(self, components: list[Component]) -> None:
        """Set up application callbacks and components."""
        super().__init__()
        self.components = components

    def get_component(self, component_id: str) -> Component | None:
        """Find a component in the application to use in callbacks."""
        for component in self.components:
            if component.id == component_id:
                return component
        return None

    def register_components(self) -> None:
        """Register all components to send value updates to callbacks."""
        for component in self.components:
            if component.id not in self._observer_map:
                return
            for property_name in component.observed_values.keys():
                if property_name not in self._observer_map[component.id]:
                    continue
                for callback in self.generate_callbacks(component.id, property_name):
                    component.observe(property_name, callback)


# Create the application to register callbacks.
app = App(
    [
        Component(id="ping"),
        Component(id="pong"),
        Component(id="other"),
    ]
)


@app.when(
    Modified("ping", "value"),  # Triggers callback.
    Select("other", "value"),  # Provides an "input" argument to the function, but does not trigger callback.
    Update("pong", "value"),  # What is updated after the callback completes.
)
def ping_pong(ping: str, other: str) -> str:
    """Basic callback that is triggered by a modified value, also accepts a basic value, and provides one update."""
    return f"ping {ping} with {other}"


@app.when(
    Modified("pong", "value"),  # Triggers callback.
    Update("other", "value"),  # Does not trigger previous callback since previous callback uses it as a collect action.
)
def pong_other(pong: str) -> str:
    """Callback that is triggered by an update from another callback, and updates a component without triggering."""
    return f"old value: {pong}"


async def main() -> None:
    """Run user prompts in async loop to allow attribute updates to trigger."""
    # Register components as capable of responding to callbacks.
    app.register_components()

    app.get_component("other").value = "foo"
    while (value := input('Enter new ping value, or "quit" to exit: ')) != "quit":
        app.get_component("ping").value = value
        await asyncio.sleep(0)
        print(app.get_component("pong").value)


if __name__ == "__main__":
    asyncio.run(main())
