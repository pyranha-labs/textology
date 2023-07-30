"""Extended Textual ProgressBar widget."""

from typing import Any

from textual import widgets

from .._extensions import WidgetExtension


class ProgressBar(WidgetExtension, widgets.ProgressBar):
    """An extended progress bar widget."""

    def __init__(
        self,
        total: float | None = None,
        *,
        show_bar: bool = True,
        show_percentage: bool = True,
        show_eta: bool = True,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        **extension_configs: Any,
    ) -> None:
        """Initialize a Progress Bar widget.

        Args:
            total: The total number of steps in the progress if known.
            show_bar: Whether to show the bar portion of the progress bar.
            show_percentage: Whether to show the percentage status of the bar.
            show_eta: Whether to show the ETA countdown of the progress bar.
            name: The name of the widget.
            id: The ID of the widget in the DOM.
            classes: The CSS classes for the widget.
            disabled: Whether the widget is disabled or not.
            extension_configs: Widget extension configurations, such as dynamically provided local callbacks by name.
        """
        super().__init__(
            total=total,
            show_bar=show_bar,
            show_percentage=show_percentage,
            show_eta=show_eta,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self.__extend_widget__(**extension_configs)
