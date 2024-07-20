"""Unit tests for widgets module."""

import asyncio
from textwrap import dedent
from typing import Callable

import pytest
from typing_extensions import override

from textology import apps
from textology import widgets


@pytest.mark.asyncio
async def test_horizontal_menu(compare_snapshots: Callable) -> None:
    """Validate basic HorizontalMenus functionality to show/hide dynamic menus."""
    app = apps.WidgetApp(
        child=widgets.HorizontalMenus(
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
    app = apps.WidgetApp(
        child=widgets.HorizontalMenus(
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
    app = apps.WidgetApp(
        child=widgets.Container(
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


@pytest.mark.asyncio
async def test_multi_select(compare_snapshots: Callable) -> None:
    """Validate basic MultiSelect functionality with allow_blank true and false combinations."""
    app = apps.WidgetApp(
        child=widgets.Vertical(
            widgets.MultiSelect(
                [
                    ("test1", "test1"),
                    ("test2", "test2"),
                    ("test3", "test3"),
                ],
                allow_blank=True,
            ),
            widgets.MultiSelect(
                [
                    ("test1", "test1"),
                    ("test2", "test2", True),
                    ("test3", "test3"),
                ],
                allow_blank=False,
            ),
        )
    )

    async with app.run_test() as pilot:
        assert all(
            [
                await compare_snapshots(
                    pilot,
                    test_suffix="idle",
                ),
                await compare_snapshots(
                    pilot,
                    press=["space", "down", "space", "down", "enter"],
                    test_suffix="with_multiple_selected",
                ),
                await compare_snapshots(
                    pilot,
                    press=["space", "up", "space", "escape"],
                    test_suffix="after_deselect_all",
                ),
                await compare_snapshots(
                    pilot,
                    press=["tab", "space", "down", "space"],
                    test_suffix="after_blocked_deselect",
                ),
            ]
        )


@pytest.mark.asyncio
async def test_modal_dialog(compare_snapshots: Callable) -> None:
    """Validate basic MultiSelect functionality with allow_blank true and false combinations."""

    def _show_dialog(_: widgets.Button.Pressed) -> None:
        dialog = widgets.ModalDialog(
            widgets.Label("Dialog Content"),
        )
        dialog.show(app)

    app = apps.WidgetApp(
        child=widgets.Vertical(
            widgets.Label("App Content"),
            widgets.Button(
                "Show Dialog",
                id="dialog-btn",
                callbacks={
                    "on_button_pressed": _show_dialog,
                },
            ),
        )
    )

    async with app.run_test() as pilot:
        snapshots = [
            await compare_snapshots(
                pilot,
                test_suffix="idle",
            ),
            await compare_snapshots(
                pilot,
                click=["#dialog-btn"],
                test_suffix="after_show",
            ),
        ]
        await asyncio.sleep(0.25)
        snapshots.append(
            await compare_snapshots(
                pilot,
                press=["escape"],
                test_suffix="after_dismiss",
            )
        )
        assert all(snapshots)


@pytest.mark.asyncio
async def test_temporary_callbacks() -> None:
    """Validate basic permanent and temporary callback functionality."""
    store = {
        "temporary": 0,
        "permanent": 0,
    }

    def _permanent_click(_: widgets.Button.Pressed) -> None:
        store["permanent"] += 1

    def _temporary_click(_: widgets.Button.Pressed) -> None:
        store["temporary"] += 1

    def _temporary_click2(_: widgets.Button.Pressed) -> None:
        store["temporary"] *= 2

    app = apps.WidgetApp(
        child=widgets.Button(
            "Clicker",
            id="clicker",
            callbacks={
                "on_button_pressed": _permanent_click,
            },
        )
    )

    async with app.run_test() as pilot:
        clicker = app.query_one("#clicker")
        clicker.add_callback(on_button_pressed=(_temporary_click, False))

        # Ensure no callbacks have been triggered.
        assert store == {
            "temporary": 0,
            "permanent": 0,
        }

        # Click twice to ensure temporary is called once, and permanent once.
        await pilot.click("#clicker")
        assert store == {
            "temporary": 1,
            "permanent": 0,
        }
        await asyncio.sleep(0.25)
        await pilot.click("#clicker")
        assert store == {
            "temporary": 1,
            "permanent": 1,
        }

        # Add another temporary clicker after usage and repeat.
        clicker.add_callback(on_button_pressed=(_temporary_click, False))
        await asyncio.sleep(0.25)
        await pilot.click("#clicker")
        assert store == {
            "temporary": 2,
            "permanent": 1,
        }
        await asyncio.sleep(0.25)
        await pilot.click("#clicker")
        assert store == {
            "temporary": 2,
            "permanent": 2,
        }

        # Add 2 temporary clickers (and attempt 1 repeat) as a list.
        clicker.add_callback(
            on_button_pressed=[
                (_temporary_click, False),
                (_temporary_click, False),  # Dropped as duplicate.
                (_temporary_click2, False),
            ]
        )
        await asyncio.sleep(0.25)
        await pilot.click("#clicker")
        assert store == {
            "temporary": 6,
            "permanent": 2,
        }
        await asyncio.sleep(0.25)
        await pilot.click("#clicker")
        assert store == {
            "temporary": 6,  # +1 then x2.
            "permanent": 3,
        }

        # Add and remove callback.
        clicker.add_callback(on_button_pressed=(_temporary_click, False))
        clicker.remove_callback(_temporary_click)
        await asyncio.sleep(0.25)
        await pilot.click("#clicker")
        assert store == {
            "temporary": 6,
            "permanent": 4,
        }


@pytest.mark.asyncio
async def test_widgets_render(compare_snapshots: Callable) -> None:
    """Validate basic widget initialization and render."""

    class Widgets(apps.App):
        @override
        def compose(self) -> apps.ComposeResult:
            text_input = widgets.TextInput("Value")
            text_input.cursor_blink = False

            tree = widgets.Tree("Tree", styles={"height": "auto"})
            tree.root.expand()
            branches = tree.root.add("Root", expand=True)
            branches.add_leaf("Branch 1")
            branches.add_leaf("Branch 2")

            with widgets.Container():
                yield widgets.Markdown(
                    dedent("""\
                    # Widget Render Tests

                    Markdown text
                    """)
                )
                yield widgets.Label("Label")
                yield widgets.Static("Static")
                yield widgets.Horizontal(
                    widgets.Label(
                        widgets.Text("Overflow left", overflow="ellipsis", overflow_side="left", no_wrap=True),
                        styles={"width": "1fr"},
                    ),
                    widgets.Label(
                        widgets.Text("Overflow right", overflow="ellipsis", overflow_side="right", no_wrap=True),
                        styles={"width": "1fr"},
                    ),
                    styles={
                        "width": 24,
                        "height": 2,
                    },
                )
                yield text_input
                yield widgets.Select([("Select 1", "1"), ("Select 2", "2")])
                yield widgets.SelectionList(("SelectionList 1", "1"), ("SelectionList 2", "2"))
                yield widgets.OptionList("OptionList 1", "OptionList 2")
                with widgets.RadioSet():
                    yield widgets.RadioButton("RadioButton 1")
                    yield widgets.RadioButton("RadioButton 2")
                with widgets.TabbedContent(initial="tab1"):
                    with widgets.TabPane("Tab 1", id="tab1"):
                        yield widgets.Label("This is tab 1.")
                    with widgets.TabPane("Tab 2", id="tab2"):
                        yield widgets.Label("This is tab 2.")
                yield widgets.Rule()
                yield tree
                with widgets.Collapsible(title="Collapsible", collapsed=False):
                    yield widgets.Label("Hello from collapsible.")
                yield widgets.DataTable()
                yield widgets.DirectoryTree("fakedir", styles={"height": "auto"})
                yield widgets.Pretty({"key1": {"key2": "value2"}})
                yield widgets.Sparkline(data=[1, 2, 3])
                yield widgets.Digits("123")
                yield widgets.ProgressBar(1)
                yield widgets.Switch(value=True)
                yield widgets.Checkbox(label="Checkbox", value=True)
                with widgets.Container(styles={"height": 4}):
                    yield widgets.TextArea.code_editor(
                        dedent("""\
                        # Comment
                        var = 123"""),
                        language="python",
                    )
                yield widgets.ContentSwitcher(
                    widgets.Label("ContentSwitcher Label 1", id="content-switcher-1"),
                    widgets.Label("ContentSwitcher Label 2", id="content-switcher-2"),
                    initial="content-switcher-2",
                )

        def on_mount(self) -> None:
            table = self.query_one(widgets.DataTable)
            table.add_columns("C1", "C2")
            table.add_rows([[1, 2]])

    async with Widgets().run_test(size=(80, 80)) as pilot:
        assert await compare_snapshots(pilot)
