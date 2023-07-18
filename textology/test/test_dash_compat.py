"""Unit tests for dash_compat module."""

import pytest

from textology import dash_compat
from textology import widgets


@pytest.mark.asyncio
async def test_button_n_clicks() -> None:
    """Validate that n_clicks increases on extended button widget click and triggers callback."""
    app = dash_compat.DashCompatApp(
        layout=widgets.Container(
            widgets.Button("Click me!", id="btn"),
            widgets.Store("Update me!", id="store1"),
            widgets.Store("Update me!", id="store2"),
        )
    )

    @app.callback(
        dash_compat.Input("btn", "n_clicks"),
        dash_compat.Output("store1", "data"),
    )
    def btn_click(n_clicks: int) -> str:
        """Basic callback on button press/click."""
        return f"Attribute callback triggered {n_clicks} times"

    @app.callback(
        dash_compat.Input("btn", widgets.Button.Pressed),
        dash_compat.Output("store2", "data"),
    )
    def btn_click_event(pressed: widgets.Button.Pressed) -> str:
        """Basic callback on button press/click."""
        return f"Event callback triggered {pressed.button.n_clicks} times"

    async with app.run_test() as pilot:
        button = app.query_one(widgets.Button)
        store1 = app.query_one("#store1")
        store2 = app.query_one("#store2")

        assert button.n_clicks == 0
        assert store1.data == "Update me!"
        assert store2.data == "Update me!"

        await pilot.click(widgets.Button)
        await pilot.click(widgets.Button)
        await pilot.click(widgets.Button)
        assert button.n_clicks == 3
        assert store1.data == "Attribute callback triggered 3 times"
        assert store2.data == "Event callback triggered 3 times"
