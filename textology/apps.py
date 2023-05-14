"""Custom textual Apps with textology extensions included."""

from __future__ import annotations

import logging
from typing import Any
from typing import Callable

from textual import events
from textual.app import App
from textual.app import ComposeResult
from textual.app import CSSPathType
from textual.containers import Container
from textual.css.query import NoMatches
from textual.driver import Driver
from textual.widget import Widget

from .logging import NullLogger
from .observers import ObserverManager
from .widgets import Location


class BrowserApp(App):
    """Application capable of routing user requests, and tracking browsing history."""

    def __init__(
        self,
        layout: Widget | None = None,
        driver_class: type[Driver] | None = None,
        css_path: CSSPathType | None = None,
        watch_css: bool = False,
    ) -> None:
        """Initialize an application with a browser history and router.

        Args:
            layout: Primary content window.
                Must contain Location widget.
            driver_class: Driver class or `None` to auto-detect.
                This will be used by some Textual tools.
            css_path: Path to CSS or `None` to use the `CSS_PATH` class variable.
                To load multiple CSS files, pass a list of strings or paths which will be loaded in order.
            watch_css: Reload CSS if the files changed.
                This is set automatically if you are using `textual run` with the `dev` switch.

        Raises:
            CssPathError: When the supplied CSS path(s) are an unexpected type.
        """
        if layout is None:
            layout = Container(
                Location(),
                Container(id="content-window"),
            )
        if isinstance(layout, Location):
            location = layout
        else:
            location = None
            for node in layout.walk_children():
                if isinstance(node, Location):
                    location = node
                    break
        if not location:
            raise ValueError("Layout must contain a Location object for routing requests")
        super().__init__(
            driver_class=driver_class,
            css_path=css_path,
            watch_css=watch_css,
        )
        self.layout = layout
        self.location = location

    def compose(self) -> ComposeResult:
        """Default compose with provided layout.

        Yields:
            Layout Widget set on instantiation.
        """
        yield self.layout

    def back(self) -> int:
        """Go back one URL in the browser history.

        Returns:
            The new index in the history.
        """
        return self.location.back()

    def forward(self) -> int:
        """Go forward one URL in the browser history.

        Returns:
            The new index in the history.
        """
        return self.location.forward()

    def get(self, url: str) -> Any:
        """Run a basic GET request against the browser.

        URL and history in browser are be updated.

        Args:
            url: Path to request.

        Returns:
            The result of handling the request.
        """
        return self.location.get(url)

    def reload(self) -> None:
        """Reload the most recent URL in the browser history."""
        self.location.reload()

    def route(self, path: str, methods: list[str] = ("GET",)) -> Callable:
        """Create a decorator that will register a path/method combination to a request callback on the browser.

        Args:
            path: Resource location that the decorated function will be allowed to respond to.
            methods: One or more methods that the decorated function will be allowed to respond to at the given path.

        Returns:
            A decorator that will register a function as capable of accepting requests to a specific path/method combo.
        """
        return self.location.route(path, methods=methods)


class ObservedApp(App, ObserverManager):
    """Application capable of performing automatic input/output callbacks on reactive widget property updates."""

    def __init__(
        self,
        driver_class: type[Driver] | None = None,
        css_path: CSSPathType | None = None,
        watch_css: bool = False,
        logger: logging.Logger | None = None,
    ) -> None:
        """Initialize an application with tracking for input/output callbacks.

        Args:
            driver_class: Driver class or `None` to auto-detect.
                This will be used by some Textual tools.
            css_path: Path to CSS or `None` to use the `CSS_PATH` class variable.
                To load multiple CSS files, pass a list of strings or paths which will be loaded in order.
            watch_css: Reload CSS if the files changed.
                This is set automatically if you are using `textual run` with the `dev` switch.
            logger: Custom logger to send callback messages to.

        Raises:
            CssPathError: When the supplied CSS path(s) are an unexpected type.
        """
        super().__init__(
            driver_class=driver_class,
            css_path=css_path,
            watch_css=watch_css,
        )
        # Manually set up observer manager mixin since App inheritance does not automatically trigger.
        ObserverManager.__init__(self, logger=logger)

    def apply_update(
        self,
        observer_id: str,
        component: Widget,
        component_id: str,
        component_property: str,
        value: Any,
    ) -> None:
        """Apply an update operation on a Widget."""
        if component_property == "children":
            # Children is a special property on widgets, it cannot be directly applied. Manually swap children.
            component.remove_children()
            if not isinstance(value, list):
                value = [value]
            component.mount_all(value)
        elif component_property == "screen":
            # Screen is a special property on applications, it cannot be directly applied. Manually add to stack.
            component.app.push_screen(value)
        else:
            super().apply_update(observer_id, component, component_id, component_property, value)

    def get_component(self, component_id: str) -> Any:
        """Fina a component in the DOM."""
        try:
            return self.query_one(f"#{component_id}")
        except NoMatches:
            return None

    def on_mount(self, _: events.Mount) -> None:
        """Ensure the logger is fully loaded after mounting."""
        if isinstance(self.logger, NullLogger):
            self.logger = self.log

    def _register_widget_observers(self, widget: Widget) -> None:
        """Enable observers for a newly added widget and its reactive attributes if it has an ID."""
        # Do not watch any widgets or properties for changes that have not had an observer set up.
        if widget.id not in self._observer_map:
            return
        for property_name in widget._reactives.keys():  # pylint: disable=protected-access
            if property_name not in self._observer_map[widget.id]:
                continue
            for callback in self.generate_callbacks(widget.id, property_name):
                self.watch(widget, property_name, callback, init=False)


def _post_mount_patch(self: Widget) -> None:
    """Called after the object has been mounted, regardless of mount event, to register observer support."""
    # Call the original function being patched to ensure the widget is fully set up before registering.
    _widget_post_mount(self)
    if self.id and hasattr(self.app, "_register_widget_observers"):
        self.app._register_widget_observers(self)  # pylint: disable=protected-access


# Patch the base Widget class to allow all reactive attributes to register to observer applications.
_widget_post_mount = Widget._post_mount  # pylint: disable=protected-access
Widget._post_mount = _post_mount_patch  # pylint: disable=protected-access
