"""Extended Textual Footer widget."""

from typing import Any

from textual import widgets

from .._extensions import WidgetExtension


class Footer(WidgetExtension, widgets.Footer):
    """A extended simple footer widget which docks itself to the bottom of the parent container."""

    def __init__(
        self,
        **extension_configs: Any,
    ) -> None:
        """Initialize the footer widget.

        Args:
            extension_configs: Widget extension configurations, such as dynamically provided local callbacks by name.
        """
        super().__init__()
        self.__extend_widget__(**extension_configs)
