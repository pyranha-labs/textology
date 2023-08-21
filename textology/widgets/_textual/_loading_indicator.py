"""Extended Textual Loading Indicator widget."""

from time import time
from typing import Any
from typing import Callable
from typing import Iterable

from textual import events
from textual import widgets
from textual.widget import Widget

from .._extensions import WidgetExtension


class LoadingIndicator(WidgetExtension, widgets.LoadingIndicator):
    """An extended display for an animated loading indicator."""

    def __init__(
        self,
        *children: Widget,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        styles: dict[str, Any] | None = None,
        disabled_messages: Iterable[events.Message] | None = None,
        callbacks: dict[str, Callable] | None = None,
    ) -> None:
        """Initialize LoadingIndicator with support for extension arguments.

        Args:
            *children: Child widgets.
            name: The name of the widget.
            id: The ID of the widget in the DOM.
            classes: The CSS classes for the widget.
            disabled: Whether the widget is disabled or not.
            styles: Local inline styles to apply on top of the class' styles for only this instance.
            disabled_messages: List of messages to disable on this widget instance only.
            callbacks: Mapping of callbacks to send messages to instead of sending to default handler.
        """
        super().__init__(
            *children,
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
        # Textual-2912: possibility of _start_time reference in render before mount due to not being declared in init.
        self._start_time = time()
