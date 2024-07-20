"""Extended Textual Pretty widget."""

from typing import Any
from typing import Iterable

from textual import events
from textual import widgets

from .._extensions import Callbacks
from .._extensions import WidgetExtension


class Pretty(widgets.Pretty, WidgetExtension):
    """An extended pretty-printing widget."""

    DEFAULT_CSS = """
    Pretty {
        height: auto;
    }
    """

    def __init__(
        self,
        obj: Any,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        styles: dict[str, Any] | None = None,
        disabled_messages: Iterable[type[events.Message]] | None = None,
        callbacks: Callbacks | None = None,
    ) -> None:
        """Initialize the Pretty widget.

        Args:
            obj: The object to pretty-print.
            name: The name of the pretty widget.
            id: The ID of the pretty in the DOM.
            classes: The CSS classes of the pretty.
            styles: Local inline styles to apply on top of the class' styles for only this instance.
            disabled_messages: List of messages to disable on this widget instance only.
            callbacks: Mapping of callbacks to send messages to instead of sending to default handler.
        """
        super().__init__(
            object=obj,
            name=name,
            id=id,
            classes=classes,
        )
        self.__extend_widget__(
            styles=styles,
            disabled_messages=disabled_messages,
            callbacks=callbacks,
        )
