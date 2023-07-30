"""Extended Textual Header widget."""

from typing import Any

from textual import widgets

from .._extensions import WidgetExtension


class Header(WidgetExtension, widgets.Header):
    """An extended header widget with icon and clock."""

    def __init__(
        self,
        show_clock: bool = False,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        **extension_configs: Any,
    ) -> None:
        """Initialize the header widget.

        Args:
            show_clock: Whether the clock should be shown on the right of the header.
            name: The name of the header widget.
            id: The ID of the header widget in the DOM.
            classes: The CSS classes of the header widget.
        """
        super().__init__(
            show_clock=show_clock,
            name=name,
            id=id,
            classes=classes,
        )
        self.__extend_widget__(**extension_configs)
