"""Custom textual Apps with textology extensions included."""

from __future__ import annotations

import logging
from collections import defaultdict
from inspect import isawaitable
from types import ModuleType
from typing import Any
from typing import Callable

from textual import events
from textual._path import _make_path_object_relative  # pylint: disable=protected-access
from textual.app import App
from textual.app import ComposeResult
from textual.app import CSSPathType
from textual.css.query import NoMatches
from textual.driver import Driver
from textual.screen import Screen
from textual.widget import Widget

from .observers import Modified
from .observers import ObserverManager
from .observers import Select
from .observers import Update
from .pages import _GLOBAL_PAGE_MAP
from .pages import Page
from .pages import register_page
from .router import Endpoint
from .router import Request
from .widgets import Container
from .widgets import Label
from .widgets import Location
from .widgets import PageContainer

_DEFAULT_CONTENT_ID = "content"
_DEFAULT_URL_ID = "url"


class LayoutApp(App):
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
        if not layout:
            layout = Container(id=_DEFAULT_CONTENT_ID)
        else:
            layout = layout() if isinstance(layout, Callable) else layout
        self.layout = layout

    def compose(self) -> ComposeResult:
        """Default compose with provided layout.

        Yields:
            Layout widget set on instantiation.
        """
        yield self.layout


class ExtendedApp(LayoutApp, ObserverManager):
    """Textual application with multiple Textology extensions for automating UI updates.

    Additional functionality:
        - Automatic input/output callbacks for managing application state via ".when()" registration.
        - URL based multi-page content via ".register_page()".
        - URL routing for resource requests within the application via ".location.get()".
        - URL history for navigating via ".back()", ".forward()", etc.
    """

    CSS_THEMES: dict[str, list[CSSPathType]] | None = None
    """Mappings of additional file paths to load CSS from in addition to base CSS."""

    def __init__(  # pylint: disable=too-many-arguments
        self,
        layout: Callable | Widget | None = None,
        use_pages: bool = False,
        pages: list[Page | ModuleType | str | Callable] | None = None,
        driver_class: type[Driver] | None = None,
        css_path: CSSPathType | None = None,
        watch_css: bool = False,
        css_theme: str | list[str] | None = None,
        css_themes: dict[str, list[CSSPathType]] | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        """Initialize an application with tracking for input/output callbacks.

        Args:
            layout: Primary content widget, or function to create primary content widget.
            use_pages: Whether to enable multi-page application support.
                When enabled, this will include automatic URL routing callbacks via "widgets.Location".
                Force enabled if "pages" are provided. Enabling without "pages" allows registering pages later.
            pages: Initial pages to load into multi-page applications.
                Refer to "register_page()" for options.
            driver_class: Driver class or `None` to auto-detect.
                This will be used by some Textual tools.
            css_path: Path to CSS or `None` to use the `CSS_PATH` class variable.
                To load multiple CSS files, pass a list of strings or paths which will be loaded in order.
            watch_css: Reload CSS if the files changed.
                This is set automatically if you are using `textual run` with the `dev` switch.
            css_theme: Initial CSS theme to load from "css_themes".
                Themes are applied in addition to base "css_path" values, rather than in place of.
            css_themes: Mapping of CSS paths by string names, or `None` to use the `CSS_THEMES` class variable.
            logger: Custom logger to send callback messages to.

        Raises:
            CssPathError: When the supplied CSS path(s) are an unexpected type.
        """
        css_path = css_path or self.CSS_PATH
        if css_path and not isinstance(css_path, list):
            css_path = [css_path]
        if css_theme and not isinstance(css_theme, list):
            css_theme = [css_theme]
        self._css_theme: list[str] = css_theme
        self.css_themes = css_themes or self.CSS_THEMES or {}
        for css_theme_name, css_theme_paths in self.css_themes.items():
            self.css_themes[css_theme_name] = [
                _make_path_object_relative(css_theme_path, self) for css_theme_path in css_theme_paths
            ]
        css_path = css_path or []
        for theme in self._css_theme or []:
            if theme in self.css_themes:
                css_path.extend(self.css_themes[theme])

        layout = layout or Container(
            Location(id=_DEFAULT_URL_ID),
            Container(id=_DEFAULT_CONTENT_ID) if not use_pages else PageContainer(id=_DEFAULT_CONTENT_ID),
        )
        super().__init__(
            layout=layout,
            driver_class=driver_class,
            css_path=css_path,
            watch_css=watch_css,
        )
        # Manually set up observer manager mixin since App inheritance does not automatically trigger.
        ObserverManager.__init__(self, logger=logger or logging.root)
        self.attach_to_observers(self)

        self._observer_message_handler_map = {}
        self._location: Location | None = None
        self._page_registry: dict[str, Page] = {}
        self._use_pages = use_pages or bool(pages)

        self.enable_pages()
        if pages:
            for page in pages:
                self.register_page(page)

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

    def apply_theme(self, theme: str | list[str] | None = None) -> None:
        """Load a CSS theme.

        Themes are applied in addition to base "css_path" values, rather than in place of.

        Args:
            theme: Name(s) of the CSS theme(s) to load from "css_themes".
                All other stylesheets not in the base CSS configuration will be unloaded.
        """
        if theme and not isinstance(theme, list):
            theme = [theme]
        css_paths = self.css_path
        stylesheet = self.stylesheet.copy()

        # Cleanup old themes first.
        for css_theme in self._css_theme or []:
            if css_theme not in self.css_themes:
                continue
            for css_theme_path in self.css_themes[css_theme]:
                if css_theme_path in css_paths:
                    css_paths.remove(css_theme_path)
                if stylesheet.has_source(css_theme_path):
                    stylesheet.source.pop(str(css_theme_path))
            self.log.info(f"Removed CSS theme: {self.css_theme}")

        # Apply new themes second.
        for css_theme in theme or []:
            if css_theme not in self.css_themes:
                self.log.error(f"CSS Theme not found: {css_theme}")
                continue
            for css_theme_path in self.css_themes.get(css_theme, []):
                css_paths.append(css_theme_path)

        # Force reload of CSS and layouts last.
        self.css_path = css_paths
        try:
            stylesheet.read_all(css_paths)
            stylesheet.parse()
            self.log.info(f"Applied theme: {theme}")
        except Exception as error:  # Do not crash app on theme swap failure. pylint: disable=broad-exception-caught
            self._css_has_errors = True
            self.log.error(error)
        else:
            self._css_theme = theme
            self._css_has_errors = False
            self.stylesheet = stylesheet
            self.refresh_css()
            for screen in self.screen_stack:
                # Must call private refresh or rendered layout may be incorrect until next screen change.
                screen._refresh_layout(self.size, full=True)  # pylint: disable=protected-access
                self.stylesheet.update(self.screen)
                self.screen.refresh(layout=True)
            self.app.refresh(layout=True)

    def back(self) -> int:
        """Go back one URL in the history.

        Returns:
            The new index in the history.
        """
        return self.location.back()

    @property
    def css_theme(self) -> list[str] | None:
        """Provide the CSS themes currently applied on top of the base CSS."""
        return self._css_theme

    @property
    def document(self) -> Screen | None:
        """Provide the base screen of the application, representing the main visible "document" in the window."""
        screens = list(self.screen_stack)
        document = screens[0] if screens else None
        return document

    def enable_pages(self) -> None:
        """Set up multi-page application routing."""
        if not self._use_pages:
            return

        location = self.location
        if not location:
            raise ValueError("Layout must contain a Location widget if pages are enabled")
        if not location.id:
            raise ValueError("Location widget must have an id if pages are enabled")

        page_container = None
        for node in self.layout.walk_children():
            if isinstance(node, PageContainer):
                page_container = node
                break
        if page_container is None:
            raise ValueError("Layout must contain a PageContainer widget if pages are enabled")
        if not page_container.id:
            raise ValueError("PageContainer widget must have an id if pages are enabled")

        # Finish final set up after all validations are performed to ensure page routing is supported.
        self.when(
            Modified(location.id, "pathname"),
            Select(location.id, "search"),
            Update(page_container.id, "children"),
        )(self._page_router)
        self.location.endpoint_not_found = Endpoint([], "", self._page_not_found)
        for page in _GLOBAL_PAGE_MAP.values():
            self.register_page(page)

    def forward(self) -> int:
        """Go forward one URL in the history.

        Returns:
            The new index in the history.
        """
        return self.location.forward()

    def get_component(self, component_id: str) -> Any:
        """Fina a component in the DOM."""
        try:
            return self.query_one(f"#{component_id}")
        except NoMatches:
            return None

    @property
    def location(self) -> Location | None:
        """Find the application's primary Location widget for routing addresses."""
        if self._location is None:
            self._update_location()
        return self._location

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

    def _page_not_found(
        self,
        request: Request,
    ) -> Label:
        """Default handler for when a request is made to a page that is not available."""
        self.logger.warning(f"Page not found {request.url.path}")
        return Label("Page not found")

    @property
    def page_registry(self) -> dict[str, Page]:
        """Provide the combined page registry in use by this multi-page application."""
        return self._page_registry.copy()

    def _page_router(self, pathname: str, search: str) -> list[Widget]:
        """Load the appropriate page based on the URL path and search options."""
        self.logger.debug(f"Routing page content for: {pathname}")

        # Simulate router "serve()" to allow error handling at the callback level instead of router/widget level.
        request = Request(pathname if not search else f"{pathname}?{search}")
        path = request.url.path
        endpoint = self.location.endpoint(path, "GET")

        # Create kwargs for the layout function based off of:
        #   - App if requested, to avoid circular imports if needed.
        #   - Original request object if requested by name, to allow full access to URL values.
        #   - Inline path variables if path is a dynamic route.
        #   - User search/query variables.
        kwargs = {}
        if "app" in endpoint.handler_vars:
            kwargs["app"] = self
        if "request" in endpoint.handler_vars:
            kwargs["request"] = request
        if not endpoint.route.static:
            kwargs.update(**endpoint.route.match_groups(path))
        kwargs.update(request.query)

        return endpoint.handler(**kwargs)

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

    def register_page(  # pylint: disable=too-many-arguments
        self,
        page: Page | ModuleType | str | Callable | None = None,
        path: str | None = None,
        name: str | None = None,
        order: int = 0,
        redirect_from: str | list[str] | None = None,
        layout: Callable | None = None,
    ) -> None:
        """Register a URL path to a layout in this multi-page application.

        Args:
            page: A module, or module path, where the remaining page's variables are defined.
                e.g. If calling from within the module itself: "__name__"
                e.g. If calling from another module: "mylib.home"
            path: URL Path, with or without variables. e.g. "/", "/home", "/documents/{document_name}"
                Inferred from the "module" or "layout" if not provided.
                    e.g. "mylib.home" -> "/home"
                    e.g. "layout_home_page" -> "/home_page"
                Variables marked as {variable_name} in paths will be passed to "layout" as keyword arguments.
            name: The name of the page link, such as what might be shown in navigation menus.
                Inferred from the "path" if not provided.
                    e.g. "home_page" -> "Home Page"
            order: The relative order to sort pages in the "page_registry", such as ordering in navigation menus.
            redirect_from: Paths that should redirect to this page's path. e.g. "/v1/home"
            layout: Function to call to generate the widget(s) used in the page's layout.
        """
        if not self._use_pages:
            raise ValueError("Pages are not enabled on this application")
        page = register_page(
            page=page,
            path=path,
            name=name,
            order=order,
            redirect_from=redirect_from,
            layout=layout,
            page_map=self._page_registry,
        )
        if page.path in ("/404", "/not_found", "/not_found_404"):
            # This is a special page that is not directly routed; it is used on every invalid path request.
            self.location.endpoint_not_found = Endpoint([], "", page.layout)
        else:
            self.route(page.path)(page.layout)

    def reload(self) -> None:
        """Reload the most recent URL in the history."""
        self.location.reload()

    def route(self, path: str, methods: list[str] = ("GET",)) -> Callable:
        """Create a decorator that will register a path/method combination to a request callback.

        Args:
            path: Resource location that the decorated function will be allowed to respond to.
            methods: One or more methods that the decorated function will be allowed to respond to at the given path.

        Returns:
            A decorator that will register a function as capable of accepting requests to a specific path/method combo.
        """
        return self.location.route(path, methods=methods)

    def _update_location(self) -> None:
        """Walk the layout tree to allow finding the application's Location widget at any point in the lifecycle."""
        for node in self.layout.walk_children():
            if isinstance(node, Location):
                self._location = node
                break


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
