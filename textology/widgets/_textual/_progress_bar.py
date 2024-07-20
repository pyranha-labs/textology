"""Extended Textual ProgressBar widget."""

from typing import Any
from typing import Iterable

from textual import events
from textual import widgets

from .._extensions import Callbacks
from .._extensions import WidgetExtension


class ProgressBar(widgets.ProgressBar, WidgetExtension):
    """An extended progress bar widget."""

    def __init__(  # pylint: disable=too-many-arguments
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
        styles: dict[str, Any] | None = None,
        disabled_messages: Iterable[type[events.Message]] | None = None,
        callbacks: Callbacks | None = None,
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
            styles: Local inline styles to apply on top of the class' styles for only this instance.
            disabled_messages: List of messages to disable on this widget instance only.
            callbacks: Mapping of callbacks to send messages to instead of sending to default handler.
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
        self.__extend_widget__(
            styles=styles,
            disabled_messages=disabled_messages,
            callbacks=callbacks,
        )
