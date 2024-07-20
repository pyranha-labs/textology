"""Widget representation of the current location of loaded resources."""

from __future__ import annotations

import logging
from typing import Any
from typing import Iterable
from urllib.parse import urlparse

from textual import events
from textual.message import Message
from textual.reactive import reactive

from textology.history import History
from textology.router import Endpoint
from textology.router import Request
from textology.router import Router

from ._extensions import Callbacks
from ._extensions import Widget


class Location(Widget, Router):
    """Hidden widget containing representation of the current location of loaded resources.

    Intended to only be used for callbacks/routing/tracking requests.
    """

    class LocationMessage(Message):
        """Base class for Location messages."""

        def __init__(
            self,
            location: Location,
        ) -> None:
            """Initialize the message.

            Args:
                location: The Location object sending the message.
            """
            super().__init__()
            self.location: Location = location

    class HistoryUpdated(LocationMessage):
        """Message sent when the location history is updated."""

    class URLUpdated(LocationMessage):
        """Message sent when the location URL changes."""

        def __init__(
            self,
            location: Location,
            old_url: str,
            new_url: str,
        ) -> None:
            """Initialize the URL update message.

            Args:
                location: The Location widget which triggered the event.
                old_url: Previously stored value.
                new_url: New stored value.
            """
            super().__init__(location=location)
            self.old_url = old_url
            self.new_url = new_url

    DEFAULT_CSS = """
    Location {
        display: none;
        width: 0;
        height: 0;
    }
    """

    # The pathname (or path) in a URL. e.g. "/path/to/resource".
    pathname: str = reactive("", repaint=False, init=False)
    # The search (or query) in URL. e.g. "?resource_type=1".
    search: str = reactive("", repaint=False, init=False)
    # The hash (or fragment) in a URL. e.g. "#resource-1".
    hash: str = reactive("", repaint=False, init=False)
    # Sentinel value used to trigger reloads from callbacks. Set to True to manually trigger a reload.
    refresh_url: bool = reactive(False, repaint=False, init=False, always_update=True)

    def __init__(  # pylint: disable=too-many-arguments
        self,
        path: str | None = "/",
        id: str | None = None,
        logger: logging.Logger | None = None,
        enable_url_events: bool = False,
        enable_history_events: bool = False,
        disabled_messages: Iterable[type[events.Message]] | None = None,
        callbacks: Callbacks | None = None,
    ) -> None:
        """Initialize the location, routing, and history.

        Args:
            path: The initial path to load after set up.
            id: The ID of the widget in the DOM.
            logger: Custom logger to send routing messages to.
            enable_url_events: Whether URL update events should be sent.
            enable_history_events: Whether history update events should be sent.
            disabled_messages: List of messages to disable on this widget instance only.
            callbacks: Mapping of callbacks to send messages to instead of sending to default handler.
        """
        super().__init__(id=id, disabled_messages=disabled_messages, callbacks=callbacks)
        self._initial_path = path
        # Manually set up router mixin since Widget inheritance does not automatically trigger.
        Router.__init__(self, logger=logger or logging.root)
        self._history = History()
        self.url_events_enabled = enable_url_events
        self.history_events_enabled = enable_history_events

    def back(self) -> int:
        """Go back in the history.

        Returns:
            The new index in the history.
        """
        old_index = self._history.index
        new_index = self._history.back()
        if new_index != old_index:
            self.update_url(self._history.value, save=False)
            self._send_history_update()
        return new_index

    def forward(self) -> int:
        """Go forward in the history.

        Returns:
            The new index in the history.
        """
        old_index = self._history.index
        new_index = self._history.forward()
        if new_index != old_index:
            self.update_url(self._history.value, save=False)
            self._send_history_update()
        return new_index

    def get(
        self,
        url: str,
    ) -> Any:
        """Run a basic GET request, and return the result.

        URL and history in browser are not updated.

        Args:
            url: Path to request.

        Returns:
            The result of handling the request.
        """
        result = self.serve(url)
        return result

    def _get_endpoint_kwargs(
        self,
        endpoint: Endpoint,
        request: Request,
    ) -> dict:
        """Collect dynamic arguments that should be sent to the endpoint based on variables in the handler."""
        kwargs = super()._get_endpoint_kwargs(endpoint, request)
        if "app" in endpoint.handler_vars:
            kwargs["app"] = self.app
        if "location" in endpoint.handler_vars:
            kwargs["location"] = self
        return kwargs

    @property
    def history(self) -> tuple[list[str], int]:
        """Provide details about the current browser history.

        Returns:
            Full browser history, and index of the current position in the history.
        """
        return self._history.values, self._history.index

    @property
    def href(self) -> str:
        """Full URL with path, search, and hash included.

        e.g. "/path/to/resource?resource_type=1#resource-1"

        Alias for "url".
        """
        return self.url

    @href.setter
    def href(self, new_value: str) -> None:
        """Update the current path, search, and hash from a full URL.

        e.g. "/path/to/resource?resource_type=1#resource-1"

        Alias for "url". Always updates history. For non-historical updates, see "update_url".
        """
        self.url = new_value

    def _on_mount(self, _: events.Mount) -> None:
        """Ensure the logger and initial path are fully loaded after mounting."""
        if self.logger == logging.root:
            self.logger = self.log
        self.url = self._initial_path

    def reload(self) -> None:
        """Reload the most recent URL in the history."""
        self.update_url(self._history.value, save=False)

    def _send_history_update(self) -> None:
        """Send a history update to registered listeners."""
        if self.history_events_enabled:
            self.post_message(self.HistoryUpdated(self))

    def _send_url_update(
        self,
        old_url: str,
        new_url: str,
    ) -> None:
        """Send a URL update to registered listeners."""
        if self.url_events_enabled:
            self.post_message(self.URLUpdated(self, old_url, new_url))

    def update_url(self, url: str, save: bool = True) -> None:
        """Update the current path, search, and hash from a URL.

        Args:
            url: Full path to location. e.g. "/path/to/resource?resource_type=1#resource-1"
            save: Whether to save the url to the history.
        """
        old_url = self.url
        parsed_url = urlparse(url)
        if self.pathname != parsed_url.path:
            self.pathname = parsed_url.path
        if self.search != parsed_url.query:
            self.search = parsed_url.query
        if self.hash != parsed_url.fragment:
            self.hash = parsed_url.fragment
        if save:
            self._history.add(url)
            self._send_history_update()
        self._send_url_update(old_url, url)

    @property
    def url(self) -> str:
        """Full URL with path, search, and hash included.

        e.g. "/path/to/resource?resource_type=1#resource-1"
        """
        href = self.pathname
        if self.search:
            href = f"{href}?{self.search}"
        if self.hash:
            href = f"{href}#{self.hash}"
        return href

    @url.setter
    def url(self, new_value: str) -> None:
        """Update the current path, search, and hash from a full URL.

        e.g. "/path/to/resource?resource_type=1#resource-1"

        Always updates history. For non-historical updates, see "update_url".
        """
        self.update_url(new_value)

    def watch_refresh_url(self, new_value: bool) -> None:
        """Monitor the sentinel attribute for refresh requests from callbacks.

        Args:
            new_value: New refresh value set on the reactive attribute.
        """
        if new_value:
            self.reload()
