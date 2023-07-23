"""Extended Textual container widgets."""

from __future__ import annotations

from typing import Any

from textual import containers
from textual.widget import Widget

from ._extensions import WidgetExtension


class Container(WidgetExtension, containers.Container):
    """An extended, simple, container widget, with vertical layout."""

    def __init__(
        self,
        *children: Widget,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        **extension_configs: Any,
    ) -> None:
        """Initialize a Container widget with extension arguments.

        Args:
            *children: Child widgets.
            name: The name of the widget.
            id: The ID of the widget in the DOM.
            classes: The CSS classes for the widget.
            disabled: Whether the widget is disabled or not.
            extension_configs: Widget extension configurations, such as dynamically provided local callbacks by name.
        """
        super().__init__(
            *children,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self.__extend_widget__(**extension_configs)


class PageContainer(Container):
    """Container used to display page contents, and signal to multi-page applications which ID to use in callbacks.

    If not used in a multi-page app, it is functionally the same as a Container.
    """
