"""Extended Textual Input widget."""

from typing import Any
from typing import Callable
from typing import Iterable

from rich.highlighter import Highlighter
from textual import events
from textual import widgets
from textual.suggester import Suggester
from textual.validation import Validator

from .._extensions import WidgetExtension


class TextInput(WidgetExtension, widgets.Input):
    """An extended text input widget.

    Renamed from "Input" to avoid conflicts with callback dependency types.
    """

    def __init__(
        self,
        value: str | None = None,
        placeholder: str = "",
        highlighter: Highlighter | None = None,
        password: bool = False,
        *,
        suggester: Suggester | None = None,
        validators: Validator | Iterable[Validator] | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        styles: dict[str, Any] | None = None,
        disabled_messages: list[type[events.Message]] | None = None,
        callbacks: dict[str, Callable] | None = None,
    ) -> None:
        """Initialize the text input widget.

        Args:
            value: An optional default value for the input.
            placeholder: Optional placeholder text for the input.
            highlighter: An optional highlighter for the input.
            password: Flag to say if the field should obfuscate its content.
            suggester: Suggester associated with this input instance.
            validators: An iterable of validators that the Input value will be checked against.
            name: Optional name for the input widget.
            id: Optional ID for the widget.
            classes: Optional initial classes for the widget.
            disabled: Whether the input is disabled or not.
            styles: Local inline styles to apply on top of the class' styles for only this instance.
            disabled_messages: List of messages to disable on this widget instance only.
            callbacks: Mapping of callbacks to send messages to instead of sending to default handler.
        """
        super().__init__(
            value=value,
            placeholder=placeholder,
            highlighter=highlighter,
            password=password,
            suggester=suggester,
            validators=validators,
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
