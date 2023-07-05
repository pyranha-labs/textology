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
            widgets.Store("Update me!", id="store"),
        )
    )

    @app.callback(
        dash_compat.Input("btn", "n_clicks"),
        dash_compat.Output("store", "data"),
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
