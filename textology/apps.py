"""Custom textual Apps with textology extensions included."""

from __future__ import annotations

import logging
from collections import defaultdict
from inspect import isawaitable
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

from .observers import ObserverManager
from .widgets import Location


class WidgetApp(App):
    """Application with a single widget for the root layout."""

    def __init__(
        self,
        layout: Callable | Widget | None = None,
        driver_class: type[Driver] | None = None,
        css_path: CSSPathType | None = None,
        watch_css: bool = False,
    ) -> None:
        """Initialize an application with a layout.

        Args:
            layout: Primary content widget, or function to create primary content widget.
            driver_class: Driver class or `None` to auto-detect.
                This will be used by some Textual tools.
            css_path: Path to CSS or `None` to use the `CSS_PATH` class variable.
                To load multiple CSS files, pass a list of strings or paths which will be loaded in order.
            watch_css: Reload CSS if the files changed.
                This is set automatically if you are using `textual run` with the `dev` switch.

        Raises:
            CssPathError: When the supplied CSS path(s) are an unexpected type.
        """
        super().__init__(
            driver_class=driver_class,
            css_path=css_path,
            watch_css=watch_css,
        )
        self.layout = layout or self.default_layout

    def compose(self) -> ComposeResult:
        """Default compose with provided layout.

        Yields:
            Layout widget set on instantiation.
        """
        yield self.layout if not isinstance(self.layout, Callable) else self.layout()

    def default_layout(self) -> Widget:
        """Default layout generator if a layout was not provided during initialization."""
        return Container(id="content-window")


class BrowserApp(WidgetApp):
    """Application capable of routing user requests, and tracking browsing history."""

    def __init__(
        self,
        layout: Callable | Widget | None = None,
        driver_class: type[Driver] | None = None,
        css_path: CSSPathType | None = None,
        watch_css: bool = False,
    ) -> None:
        """Initialize an application with a browser history and router.

        Args:
            layout: Primary content widget, or function to create primary content widget.
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
        elif isinstance(layout, Callable):
            layout = layout()

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
            layout=layout,
            driver_class=driver_class,
            css_path=css_path,
            watch_css=watch_css,
        )
        self.location = location

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


class ObservedApp(WidgetApp, ObserverManager):
    """Application capable of performing automatic input/output callbacks on reactive widget property updates."""

    def __init__(
        self,
        layout: Callable | Widget | None = None,
        driver_class: type[Driver] | None = None,
        css_path: CSSPathType | None = None,
        watch_css: bool = False,
        logger: logging.Logger | None = None,
    ) -> None:
        """Initialize an application with tracking for input/output callbacks.

        Args:
            layout: Primary content widget, or function to create primary content widget.
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
            layout=layout,
            driver_class=driver_class,
            css_path=css_path,
            watch_css=watch_css,
        )
        # Manually set up observer manager mixin since App inheritance does not automatically trigger.
        ObserverManager.__init__(self, logger=logger or logging.root)
        self._observer_message_handler_map = {}

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
            if value:
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

    async def _on_message(self, message: events.Message) -> None:
        """Process messages after sending to registered observers first."""
        control = message.control
        if control:
            controller_id = control.id
            if controller_id:
                cls = message.__class__
                callbacks = self._observer_message_handler_map.get(f"{controller_id}@{cls.__module__}.{cls.__name__}")
                if callbacks:
                    for callback in callbacks:
                        result = callback(None, message)
                        if isawaitable(result):
                            await result
        await super()._on_message(message)

    def on_mount(self, _: events.Mount) -> None:
        """Ensure the widget and observers are fully loaded after mounting."""
        if self.logger == logging.root:
            self.logger = self.log

        # Combine global observers with local observers outside init, so that apps can be declared anywhere in modules.
        combined_observer_map = defaultdict(lambda: defaultdict(list))
        for observer_map in (self._observer_map, self._observer_map_global):
            for widget_id, property_map in observer_map.items():
                for property_id, observers in property_map.items():
                    combined_observer_map[widget_id][property_id].extend(observers)

        # Register event watchers.
        for widget_id, property_map in combined_observer_map.items():
            for property_id, observers in property_map.items():
                for observer in observers:
                    if observer.publications:
                        self._observer_message_handler_map.setdefault(f"{widget_id}@{property_id}", []).append(
                            self._generate_callback(
                                widget_id,
                                property_id,
                                observer,
                            )
                        )
        self.attach_to_observers(self)

    def _register_reactive_observers(self, widget: Widget) -> None:
        """Enable observers for a newly added widget and its reactive attributes if it has an ID."""
        # Do not watch any widgets or properties for changes that have not had an observer set up.
        widget_id = widget.id
        if not widget_id or (widget_id not in self._observer_map and widget_id not in self._observer_map_global):
            return
        for property_name in widget._reactives.keys():  # pylint: disable=protected-access
            if (
                property_name not in self._observer_map[widget_id]
                and property_name not in self._observer_map_global[widget_id]
            ):
                continue
            for callback in self.generate_callbacks(widget_id, property_name):
                self.watch(widget, property_name, callback, init=False)


def _post_mount_patch(self: Widget) -> None:
    """Called after the object has been mounted, regardless of mount event, to register observer support."""
    # Call the original function being patched to ensure the widget is fully set up before registering.
    _widget_post_mount(self)
    attach_to_observers = getattr(self.app, "attach_to_observers", None)
    if attach_to_observers:
        attach_to_observers(self)
    if self.id:
        _register_reactive_observers = getattr(self.app, "_register_reactive_observers", None)
        if _register_reactive_observers:
            _register_reactive_observers(self)


# Patch the base Widget class to allow all reactive attributes to register to observer applications.
_widget_post_mount = Widget._post_mount  # pylint: disable=protected-access
Widget._post_mount = _post_mount_patch  # pylint: disable=protected-access
