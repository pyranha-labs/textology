"""Extended Textual RadioSet widget."""

from typing import Any
from typing import Iterable

from textual import events
from textual import widgets

from .._extensions import Callbacks
from .._extensions import WidgetExtension


class RadioSet(widgets.RadioSet, WidgetExtension):
    """Widget for grouping a collection of radio buttons into a set."""

    def __init__(
        self,
        *buttons: str | widgets.RadioButton,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        styles: dict[str, Any] | None = None,
        disabled_messages: Iterable[type[events.Message]] | None = None,
        callbacks: Callbacks | None = None,
    ) -> None:
        """Initialize the radio set.

        Args:
            buttons: A collection of labels or "RadioButton"(s) to group together.
            name: The name of the radio set.
            id: The ID of the radio set in the DOM.
            classes: The CSS classes of the radio set.
            disabled: Whether the radio set is disabled or not.
            styles: Local inline styles to apply on top of the class' styles for only this instance.
            disabled_messages: List of messages to disable on this widget instance only.
            callbacks: Mapping of callbacks to send messages to instead of sending to default handler.
        """
        super().__init__(
            *buttons,
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
