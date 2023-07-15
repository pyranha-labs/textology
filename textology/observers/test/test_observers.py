"""Unit tests for callbacks module."""

import asyncio

import pytest

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


@pytest.mark.asyncio
async def test_callback_chain() -> None:
    """Basic unit test to validate manual and automatic trigger on components."""
    app = App(
        [
            Component(id="ping"),
            Component(id="pong"),
            Component(id="other"),
        ]
    )

    @app.when(
        Modified("ping", "value"),
        Select("other", "value"),
        Update("pong", "value"),
    )
    async def ping_pong(ping: str, other: str) -> str:
        """Basic callback that is triggered by a modified value, also accepts a basic value, and provides one update."""
        return f"ping {ping} with {other}"

    @app.when(
        Modified("pong", "value"),
        Update("other", "value"),
    )
    async def pong_other(pong: str) -> str:
        """Callback that is triggered by an update from another callback, and updates a component without triggering."""
        return f"other value: {pong}"

    app.register_components()

    ping_comp = app.get_component("ping")
    pong_comp = app.get_component("pong")
    other_comp = app.get_component("other")

    assert ping_comp.value is None
    assert pong_comp.value is None
    assert other_comp.value is None

    ping_comp.value = "test1"
    await asyncio.sleep(0.1)
    assert ping_comp.value == "test1"
    assert pong_comp.value == "ping test1 with None"
    assert other_comp.value == "other value: ping test1 with None"

    ping_comp.value = "test2"
    await asyncio.sleep(0.1)
    assert ping_comp.value == "test2"
    assert pong_comp.value == "ping test2 with other value: ping test1 with None"
    assert other_comp.value == "other value: ping test2 with other value: ping test1 with None"


@pytest.mark.asyncio
async def test_callback_without_output() -> None:
    """Validate that a callback was triggered, even if no output."""
    app = App(
        [
            Component(id="ping"),
        ]
    )

    called = False

    @app.when(
        Modified("ping", "value"),
    )
    async def ping_pong(ping: str) -> None:
        """Basic callback that is triggered by a modified value, but has no output."""
        nonlocal called
        called = True

    app.register_components()

    ping_comp = app.get_component("ping")
    assert ping_comp.value is None
    assert not called

    ping_comp.value = "test1"
    await asyncio.sleep(0.1)
    assert ping_comp.value == "test1"
    assert called
