"""Extended Textual Sparkline widget."""

from typing import Any
from typing import Callable
from typing import Sequence

from textual import widgets

from .._extensions import WidgetExtension


class Sparkline(WidgetExtension, widgets.Sparkline):
    """An extended sparkline widget to display numerical data."""

    def __init__(
        self,
        data: Sequence[float] | None = None,
        *,
        summary_function: Callable[[Sequence[float]], float] | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        **extension_configs: Any,
    ) -> None:
        """Initialize a sparkline widget.

        Args:
            data: The initial data to populate the sparkline with.
            summary_function: Summarises bar values into a single value used to
                represent each bar.
            name: The name of the widget.
            id: The ID of the widget in the DOM.
            classes: The CSS classes for the widget.
            disabled: Whether the widget is disabled or not.
            extension_configs: Widget extension configurations, such as dynamically provided local callbacks by name.
        """
        super().__init__(
            data,
            summary_function=summary_function,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self.__extend_widget__(**extension_configs)
