"""Widget container for basic data storage and sharing between callbacks."""

from __future__ import annotations

import time
from typing import Any
from typing import Iterable
from typing import TypeVar

from textual import events
from textual.reactive import reactive

from ._extensions import Callbacks
from ._extensions import Widget

JsonType = TypeVar("JsonType", dict, list, bool, float, int, str, None)  # Custom type. pylint: disable=invalid-name


class Store(Widget):
    """Hidden widget for basic data storage.

    Intended to only be used for sharing data between callbacks.
    """

    DEFAULT_CSS = """
    Store {
        display: none;
        width: 0;
        height: 0;
    }
    """

    # The currently stored data.
    data: JsonType = reactive(None, repaint=False, init=False)
    # The timestamp from the last time the value was modified.
    modified_timestamp: float = reactive(-1.0, repaint=False, init=False)
    # Sentinel value used to trigger clears from callbacks. Set to True to manually trigger a clear.
    clear_data: bool = reactive(False, always_update=True, repaint=False, init=False)

    class Updated(events.Message):
        """Posted when the backend data is updated."""

        def __init__(self, store: Store, data: Any, modified_timestamp: float) -> None:
            """Initialize the data update event.

            Args:
                store: The store that sent the event.
                data: The new data stored.
                modified_timestamp: When the data was modified.
            """
            super().__init__()
            self.store = store
            self.data = data
            self.modified = modified_timestamp

        @property
        def control(self) -> Store:
            """The store that contains the data."""
            return self.store

    def __init__(
        self,
        data: Any = None,
        id: str | None = None,
        disabled_messages: Iterable[type[events.Message]] | None = None,
        callbacks: Callbacks | None = None,
    ) -> None:
        """Initialize the data store.

        Args:
            data: Initial data to store.
            id: The ID of the widget in the DOM.
            disabled_messages: List of messages to disable on this widget instance only.
            callbacks: Mapping of callbacks to send messages to instead of sending to default handler.
        """
        super().__init__(id=id, disabled_messages=disabled_messages, callbacks=callbacks)
        self.data = data

    def watch_clear_data(self, new_value: bool) -> None:
        """Monitor the sentinel attribute for clear data requests from callbacks.

        Args:
            new_value: New clear data value set on the reactive attribute.
        """
        if new_value:
            self.data = None

    def watch_data(self, _: JsonType) -> None:
        """Monitor the data in order to update the modified timestamp."""
        self.modified_timestamp = time.time()
        self.post_message(self.Updated(self, self.data, self.modified_timestamp))
