"""Extended Textual Footer widget."""

from typing import Any
from typing import Callable

from textual import events
from textual import widgets

from .._extensions import WidgetExtension


class Footer(WidgetExtension, widgets.Footer):
    """An extended simple footer widget which docks itself to the bottom of the parent container."""

    def __init__(
        self,
        styles: dict[str, Any] | None = None,
        disabled_messages: list[type[events.Message]] | None = None,
        callbacks: dict[str, Callable] | None = None,
    ) -> None:
        """Initialize the footer widget.

        Args:
            styles: Local inline styles to apply on top of the class' styles for only this instance.
            disabled_messages: List of messages to disable on this widget instance only.
            callbacks: Mapping of callbacks to send messages to instead of sending to default handler.
        """
        super().__init__()
        self.__extend_widget__(
            styles=styles,
            disabled_messages=disabled_messages,
            callbacks=callbacks,
        )
