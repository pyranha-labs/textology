"""Unit tests for apps module."""

from pathlib import Path
from typing import Callable

import pytest
from textual.app import ComposeResult

from textology import apps
from textology import observers
from textology import widgets
from textology.test import basic_app

SNAPSHOT_DIR = Path(Path(__file__).parent, "snapshots")


@pytest.mark.asyncio
async def test_button_n_clicks() -> None:
    """Validate that n_clicks increases on extended button widget click and triggers callback."""
    app = basic_app.BasicApp()

    @app.when(
        observers.Modified("btn", "n_clicks"),
        observers.Update("store", "data"),
    )
    def btn_click(clicks: int) -> str:
        return f"Button clicked {clicks} times"

    async with app.run_test() as pilot:
        button = app.query_one(widgets.Button)
        store = app.query_one(widgets.Store)
        assert button.n_clicks == 0
        assert store.data == "Update me!"

        await pilot.click(widgets.Button)
        await pilot.click(widgets.Button)
        await pilot.click(widgets.Button)
        assert button.n_clicks == 3
        assert store.data == "Button clicked 3 times"


@pytest.mark.asyncio
async def test_snapshot_with_app(compare_snapshots: Callable) -> None:
    """Validate that snapshot fixture/test works with instantiated app."""
    assert await compare_snapshots(basic_app.BasicApp(), Path(SNAPSHOT_DIR, "test_basic_app.svg"))


@pytest.mark.asyncio
async def test_snapshot_with_module(compare_snapshots: Callable) -> None:
    """Validate that snapshot fixture/test works with module containing an app."""
    assert await compare_snapshots(basic_app, Path(SNAPSHOT_DIR, "test_basic_app.svg"))


@pytest.mark.asyncio
async def test_snapshot_with_pilot(compare_snapshots: Callable) -> None:
    """Validate that snapshot fixture/test works with instantiated pilot."""
    async with basic_app.BasicApp().run_test() as pilot:
        assert await compare_snapshots(pilot, Path(SNAPSHOT_DIR, "test_basic_app.svg"))


@pytest.mark.asyncio
async def test_callback_registration_per_scope(compare_snapshots: Callable) -> None:
    """Validate that observer/callback registration works at all scopes."""

    class DisplayWidget(widgets.ExtendedWidget):
        """Widget used to test callbacks attached at a widget level."""

        def compose(self) -> ComposeResult:
            yield widgets.Store([], id="results")
            yield widgets.Label("No Data", id="display")

        @observers.when(
            observers.Modified("results", "data"),
        )
        def update_label(self, results: list) -> None:
            self.app.query_one("#display").update("\n".join(results))

    class App(apps.ExtendedApp):
        """Application used to test callbacks attached at an application level."""

        def compose(self) -> ComposeResult:
            yield widgets.Button("Button 1", id="btn1")
            yield widgets.Button("Button 2", id="btn2")
            yield widgets.Button("Button 3", id="btn3")
            yield widgets.Button("Button 4", id="btn4")
            yield DisplayWidget(styles={"height": "auto"})

        @observers.when(
            observers.Modified("btn1", "n_clicks"),
            observers.Select("results", "data"),
            observers.Update("results", "data"),
        )
        def method_reactive(self, clicks: int, results: list) -> list:
            results = [*results, f"Button 1 pressed {clicks} times"]
            return results

        @observers.when(
            observers.Published("btn3", widgets.Button.Pressed),
            observers.Select("results", "data"),
            observers.Update("results", "data"),
        )
        def method_event(self, event: widgets.Button.Pressed, results: list) -> list:
            results = [*results, f"Button 3 pressed {event.button.n_clicks} times"]
            return results

    @observers.when(
        observers.Modified("btn2", "n_clicks"),
        observers.Select("results", "data"),
        observers.Update("results", "data"),
    )
    def function_reactive(clicks: int, results: list) -> list:
        results = [*results, f"Button 2 pressed {clicks} times"]
        return results

    @observers.when(
        observers.Published("btn4", widgets.Button.Pressed),
        observers.Select("results", "data"),
        observers.Update("results", "data"),
    )
    def function_event(event: widgets.Button.Pressed, results: list) -> list:
        results = [*results, f"Button 4 pressed {event.button.n_clicks} times"]
        return results

    async with App().run_test() as pilot:
        await pilot.click("#btn1")
        await pilot.click("#btn2")
        await pilot.click("#btn3")
        await pilot.click("#btn4")
        assert await compare_snapshots(pilot)
