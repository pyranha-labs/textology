"""Widget container for basic data storage and sharing between callbacks."""

import time
from typing import Any
from typing import TypeVar

from textual.reactive import reactive
from textual.widget import Widget

from ._extensions import WidgetInitExtension

JsonType = TypeVar("JsonType", dict, list, bool, float, int, str, None)  # Custom type. pylint: disable=invalid-name


class Store(WidgetInitExtension, Widget):
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

    def __init__(
        self,
        data: Any,
        id: str | None = None,
        **extension_configs: Any,
    ) -> None:
        """Initialize the data store.

        Args:
            data: Initial data to store.
            id: The ID of the widget in the DOM.
            extension_configs: Widget extension configurations, such as dynamically provided local callbacks by name.
        """
        super().__init__(id=id, **extension_configs)
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
