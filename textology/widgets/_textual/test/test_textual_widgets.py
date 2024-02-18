"""Unit tests for textual widgets module."""

from typing import Callable

import pytest
from textual import containers

from textology import apps
from textology import widgets


@pytest.mark.asyncio
async def test_containers(compare_snapshots: Callable) -> None:
    """Validate all extended container types render correctly, similar to native containers."""
    app = apps.WidgetApp(
        widgets.Container(
            # Native containers.
            containers.Horizontal(
                widgets.Label("Horizontal1"),
                widgets.Label("Horizontal2"),
                containers.Center(
                    widgets.Label("Center1"),
                    widgets.Label("Center2"),
                ),
                containers.Vertical(
                    containers.Middle(
                        widgets.Label("Middle1"),
                        widgets.Label("Middle2"),
                    ),
                ),
            ),
            # Extended containers.
            widgets.Horizontal(
                widgets.Label("Horizontal1"),
                widgets.Label("Horizontal2"),
                widgets.Center(widgets.Label("Center1"), widgets.Label("Center2"), styles={"background": "orange"}),
                widgets.Vertical(
                    widgets.Middle(
                        widgets.Label("Middle1"),
                        widgets.Label("Middle2"),
                    ),
                    styles={"background": "blue"},
                ),
                styles={"background": "green"},
            ),
        )
    )

    async with app.run_test() as pilot:
        await compare_snapshots(pilot)
