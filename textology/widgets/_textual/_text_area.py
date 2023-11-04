"""Extended Textual TextArea widget."""

from typing import Any
from typing import Callable

from textual import events
from textual import widgets

from .._extensions import WidgetExtension


class TextArea(WidgetExtension, widgets.TextArea):
    """An extended multi-line text input widget."""

    def __init__(  # pylint: disable=too-many-arguments
        self,
        text: str = "",
        *,
        language: str | None = None,
        theme: str | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        styles: dict[str, Any] | None = None,
        disabled_messages: list[type[events.Message]] | None = None,
        callbacks: dict[str, Callable] | None = None,
    ) -> None:
        """Initialize the text area widget.

        Args:
            text: The initial text to load into the TextArea.
            language: The language to use.
            theme: The theme to use.
            name: The name of the collapsible.
            id: The ID of the widget in the DOM.
            classes: The CSS classes of the widget.
            disabled: Whether the widget is disabled or not.
            styles: Local inline styles to apply on top of the class' styles for only this instance.
            disabled_messages: List of messages to disable on this widget instance only.
            callbacks: Mapping of callbacks to send messages to instead of sending to default handler.
        """
        super().__init__(
            text=text,
            language=language,
            theme=theme,
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
