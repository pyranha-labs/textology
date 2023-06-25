"""Unit tests for apps module."""

from pathlib import Path
from typing import Callable

import pytest

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
    def btn_click(n_clicks: int) -> str:
        """Basic callback on button press/click."""
        return f"Button clicked {n_clicks} times"

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
