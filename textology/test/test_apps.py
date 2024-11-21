"""Unit tests for apps module."""

import asyncio
from pathlib import Path

import pytest
from textual.app import ComposeResult

from textology import apps
from textology import observers
from textology import widgets
from textology.pytest_utils import CompareSnapshotsFixture
from textology.test import basic_app
from textology.test import basic_themed_app

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
        await asyncio.sleep(0.25)
        await pilot.click(widgets.Button)
        await asyncio.sleep(0.25)
        await pilot.click(widgets.Button)
        assert button.n_clicks == 3
        assert store.data == "Button clicked 3 times"


@pytest.mark.asyncio
async def test_extended_app(compare_snapshots: CompareSnapshotsFixture) -> None:
    """Validate generic extended application behavior."""
    async with apps.ExtendedApp().run_test() as pilot:
        # Validate the application adds the default content container.
        await pilot.app.query_one("#content").mount(widgets.Label("Added to default"))
        assert await compare_snapshots(pilot, test_suffix="default_child")

        # Validate that the application contains the correct document root.
        assert pilot.app.document == pilot.app.screen_stack[0]

    with pytest.raises(ValueError):
        async with apps.ExtendedApp(child=widgets.Label("Extended app content"), use_pages=False).run_test() as pilot:
            # Validate that the application raises if pages are not enabled, and one is attempted to be added.
            pilot.app.register_page()

    with pytest.raises(ValueError):
        async with apps.ExtendedApp(child=widgets.Label("Extended app content"), use_pages=True).run_test() as pilot:
            # Validate that the application raises if pages enabled, but no location element in document.
            pilot.app.enable_pages()

    with pytest.raises(ValueError):
        async with apps.ExtendedApp(
            child=widgets.Container(
                widgets.Label("Extended app content"),
                widgets.Location(),
            ),
            use_pages=True,
        ).run_test() as pilot:
            # Validate that the application raises if pages enabled, and location is missing an id.
            pilot.app.enable_pages()

    async with apps.ExtendedApp(use_pages=True).run_test() as pilot:
        await pilot.app.query_one("#content").mount(widgets.Label("Added to default"))
        # Validate there are no pages registered on start.
        assert pilot.app.page_registry == {}

        # Validate that the application loads a missing content page when invalid route is used.
        pilot.app.location.url = "/bad-route"
        assert await compare_snapshots(pilot, test_suffix="bad_route")


@pytest.mark.asyncio
async def test_extended_app_page_cache(compare_snapshots: CompareSnapshotsFixture) -> None:
    """Validate page cached on extended application behavior."""
    app = apps.ExtendedApp(
        widgets.Horizontal(
            widgets.Container(
                widgets.Label(
                    "Side bar",
                )
            ),
            widgets.Container(
                widgets.Location(id="url"),
                widgets.PageContainer(id="content"),
            ),
        ),
        use_pages=True,
        cache_pages=True,
    )

    def layout_page1() -> widgets.Widget:
        return widgets.Container(
            widgets.Label("Page 1"),
            widgets.TextInput(id="input1", placeholder="Page 1 Input"),
        )

    def layout_page2() -> widgets.Widget:
        return widgets.Container(
            widgets.Label("Page 2"),
            widgets.TextInput(id="input2", placeholder="Page 2 Input"),
        )

    app.register_page(layout_page1, path="/page1")
    app.register_page(layout_page2, path="/page2")

    async with app.run_test() as pilot:
        app.location.pathname = "/page1"
        await asyncio.sleep(0.25)
        app.set_focus(app.query_one("#input1"))
        await pilot.press("t", "1")
        assert await compare_snapshots(pilot, test_suffix="page1")

        app.location.pathname = "/page2"
        await asyncio.sleep(0.25)
        app.set_focus(app.query_one("#input2"))
        await pilot.press("t", "2")
        assert await compare_snapshots(pilot, test_suffix="page2")

        app.location.pathname = "/page1"
        await asyncio.sleep(0.25)
        assert await compare_snapshots(pilot, test_suffix="page1_cached")


@pytest.mark.asyncio
async def test_snapshot_with_app(compare_snapshots: CompareSnapshotsFixture) -> None:
    """Validate that snapshot fixture/test works with instantiated app."""
    assert await compare_snapshots(basic_app.BasicApp(), Path(SNAPSHOT_DIR, "test_basic_app.svg"))


@pytest.mark.asyncio
async def test_snapshot_with_module(compare_snapshots: CompareSnapshotsFixture) -> None:
    """Validate that snapshot fixture/test works with module containing an app."""
    assert await compare_snapshots(basic_app, Path(SNAPSHOT_DIR, "test_basic_app.svg"))


@pytest.mark.asyncio
async def test_snapshot_with_pilot(compare_snapshots: CompareSnapshotsFixture) -> None:
    """Validate that snapshot fixture/test works with instantiated pilot."""
    async with basic_app.BasicApp().run_test() as pilot:
        assert await compare_snapshots(pilot, Path(SNAPSHOT_DIR, "test_basic_app.svg"))


@pytest.mark.asyncio
async def test_callback_registration_per_scope(compare_snapshots: CompareSnapshotsFixture) -> None:
    """Validate that observer/callback registration works at all scopes."""

    class DisplayWidget(widgets.Widget):
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
        await asyncio.sleep(0.25)
        assert await compare_snapshots(pilot)


@pytest.mark.asyncio
async def test_multi_page_app(compare_snapshots: CompareSnapshotsFixture) -> None:
    """Validate that multi-page application routes successfully between pages on URL changes."""

    def layout_page1(clicks: int | None = None) -> widgets.Label:
        return widgets.Label(f"Page 1 clicks {clicks}")

    def layout_page2(clicks: int | None = None) -> widgets.Label:
        return widgets.Label(f"Page 2 clicks {clicks}")

    app = apps.ExtendedApp(
        child=widgets.Container(
            widgets.Button("Button 1", id="btn1"),
            widgets.Button("Button 2", id="btn2"),
            widgets.Location(id="url"),
            widgets.PageContainer(id="content"),
        ),
        pages=[
            # Test page on initialization with no path variables.
            layout_page1
        ],
    )

    # Test page after initialization with path variables.
    app.register_page(path="/page2/{clicks}", layout=layout_page2)

    @app.when(
        observers.Modified("btn1", "n_clicks"),
        observers.Update("url", "href"),
    )
    def btn1_click(clicks: int) -> str:
        return f"/page1?clicks={clicks}"

    @app.when(
        observers.Modified("btn2", "n_clicks"),
        observers.Update("url", "href"),
    )
    def btn1_click(clicks: int) -> str:
        return f"/page2/{clicks}"

    async with app.run_test() as pilot:
        await pilot.click("#btn1")
        await compare_snapshots(pilot, test_suffix="page1")
        await asyncio.sleep(0.25)
        await pilot.click("#btn2")
        await compare_snapshots(pilot, test_suffix="page2")

        # Test selections and tracking without using buttons.
        assert app.current_page == "/page2/1"
        with pytest.raises(ValueError):
            app.select_page("/bad_page")
        app.select_page("/page1?clicks=123")
        await asyncio.sleep(0.25)
        assert app.current_page == "/page1"
        await compare_snapshots(pilot, test_suffix="select_page1")
        app.select_page("/page2/123")
        await asyncio.sleep(0.25)
        assert app.current_page == "/page2/123"
        await compare_snapshots(pilot, test_suffix="select_page2")
        await compare_snapshots(compare_results=True)


@pytest.mark.asyncio
async def test_themed_app(compare_snapshots: CompareSnapshotsFixture) -> None:
    """Test basic behavior of CSS themed apps."""
    async with basic_themed_app.BasicThemedApp(
        css_path="basic_themed_app-white_border.css",
    ).run_test() as pilot:
        assert await compare_snapshots(pilot, test_suffix="manual_css_path")

    async with basic_themed_app.BasicThemedApp(
        css_theme="white",
    ).run_test() as pilot:
        assert await compare_snapshots(pilot, test_suffix="manual_css_theme")

    async with basic_themed_app.BasicThemedApp().run_test() as pilot:
        await compare_snapshots(pilot, test_suffix="no_theme")

        pilot.app.apply_theme("green")
        await compare_snapshots(pilot, test_suffix="green")

        pilot.app.apply_theme("white")
        await compare_snapshots(pilot, test_suffix="white")

        pilot.app.apply_theme(["green", "white"])
        await compare_snapshots(pilot, test_suffix="green_white")

        # Test 1 final reset back to no theme.
        pilot.app.apply_theme(None)
        await compare_snapshots(pilot, test_suffix="no_theme")

        await compare_snapshots(compare_results=True)


@pytest.mark.asyncio
async def test_widget_app(compare_snapshots: CompareSnapshotsFixture) -> None:
    """Validate generic widget application behavior."""
    async with apps.WidgetApp().run_test() as pilot:
        # Validate the application adds the default content container.
        await pilot.app.query_one("#content").mount(widgets.Label("Added to default"))
        assert await compare_snapshots(pilot, test_suffix="default_child")
