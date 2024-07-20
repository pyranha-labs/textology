"""Extended Textual Switch widget."""

from typing import Any
from typing import Iterable

from textual import events
from textual import widgets

from .._extensions import Callbacks
from .._extensions import WidgetExtension


class Switch(widgets.Switch, WidgetExtension):
    """An extended switch widget that represents a boolean value."""

    def __init__(
        self,
        value: bool = False,
        *,
        animate: bool = True,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        styles: dict[str, Any] | None = None,
        disabled_messages: Iterable[type[events.Message]] | None = None,
        callbacks: Callbacks | None = None,
    ) -> None:
        """Initialize the switch.

        Args:
            value: The initial value of the switch.
            animate: True if the switch should animate when toggled.
            name: The name of the switch.
            id: The ID of the switch in the DOM.
            classes: The CSS classes of the switch.
            disabled: Whether the switch is disabled or not.
            styles: Local inline styles to apply on top of the class' styles for only this instance.
            disabled_messages: List of messages to disable on this widget instance only.
            callbacks: Mapping of callbacks to send messages to instead of sending to default handler.
        """
        super().__init__(
            value,
            animate=animate,
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
