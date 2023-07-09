"""Unit tests for widgets module."""

from typing import Callable

import pytest

from textology import apps
from textology import widgets


@pytest.mark.asyncio
async def test_horizontal_menu(compare_snapshots: Callable) -> None:
    """Validate basic HorizontalMenus functionality to show/hide dynamic menus."""
    app = apps.WidgetApp(
        layout=widgets.Container(
            widgets.HorizontalMenus(
                widgets.ListItemMeta(data={"label": "Page 1"}),
                widgets.ListItemMeta(
                    data={
                        "label": "Page 2",
                        "menu_items": [
                            widgets.ListItemMeta(widgets.ListItemHeader, data={"label": "Page 2"}),
                            widgets.ListItemMeta(data={"label": "Page 2 Item 1"}),
                            widgets.ListItemMeta(data={"label": "Page 2 Item 2"}),
                        ],
                    }
                ),
                widgets.ListItemMeta(
                    data={
                        "label": "Page 3",
                        "menu_items": [
                            widgets.ListItemMeta(widgets.ListItemHeader, data={"label": "Page 3"}),
                            widgets.ListItemMeta(data={"label": "Page 3 Item 1"}),
                            widgets.ListItemMeta(
                                data={
                                    "label": "Page 3 Item 2",
                                    "menu_items": [
                                        widgets.ListItemMeta(widgets.ListItemHeader, data={"label": "Page 3 Item 2"}),
                                        widgets.ListItemMeta(data={"label": "Page 3 Item 2 Sub 1"}),
                                        widgets.ListItemMeta(data={"label": "Page 3 Item 2 Sub 2"}),
                                    ],
                                }
                            ),
                        ],
                    }
                ),
            ),
            styles={"layout": "horizontal"},
        )
    )

    async with app.run_test() as pilot:
        assert all(
            [
                await compare_snapshots(pilot, test_suffix="page1"),
                await compare_snapshots(pilot, press=["down"], test_suffix="page2"),
                await compare_snapshots(pilot, press=["down", "right", "down"], test_suffix="page3"),
            ]
        )
