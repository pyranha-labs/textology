"""Unit tests for widgets module."""

from typing import Callable

import pytest

from textology import apps
from textology import widgets


@pytest.mark.asyncio
async def test_horizontal_menu(compare_snapshots: Callable) -> None:
    """Validate basic HorizontalMenus functionality to show/hide dynamic menus."""
    app = apps.LayoutApp(
        layout=widgets.HorizontalMenus(
            widgets.ListItemHeader(widgets.Label("Pages")),
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


@pytest.mark.asyncio
async def test_horizontal_menu_with_listview(compare_snapshots: Callable) -> None:
    """Validate basic HorizontalMenus functionality when a pre-populated Listview is provided, instead of ListItems."""
    app = apps.LayoutApp(
        layout=widgets.HorizontalMenus(
            widgets.ListView(
                widgets.ListItemHeader(widgets.Label("Pages")),
                widgets.ListItem(
                    data={
                        "label": "Page 1",
                        "menu_items": [
                            widgets.ListItemMeta(widgets.ListItemHeader, data={"label": "Page 1"}),
                            widgets.ListItemMeta(data={"label": "Page 1 Item 1"}),
                            widgets.ListItemMeta(data={"label": "Page 1 Item 2"}),
                        ],
                    }
                ),
                widgets.ListItem(
                    data={
                        "label": "Page 2",
                    }
                ),
            ),
        )
    )

    async with app.run_test() as pilot:
        assert all(
            [
                await compare_snapshots(pilot, press=["right", "down"]),
            ]
        )


@pytest.mark.asyncio
async def test_list_items(compare_snapshots: Callable) -> None:
    """Validate all ListItem types and combinations render correctly."""
    app = apps.LayoutApp(
        layout=widgets.Container(
            widgets.ListView(
                widgets.ListItemHeader(widgets.Label("Header From Widget")),
                widgets.ListItemHeader(data={"label": "Header From Label"}),
                widgets.ListItemHeader(name="Header from Name"),
                widgets.ListItem(widgets.Label("Item From Widget")),
                widgets.ListItem(data={"label": "Item from Label"}),
                widgets.ListItem(name="Item from Name"),
            )
        )
    )

    async with app.run_test() as pilot:
        assert all(
            [
                await compare_snapshots(pilot),
            ]
        )
