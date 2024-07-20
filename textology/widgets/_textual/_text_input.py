"""Extended Textual Input widget."""

from typing import Any
from typing import Iterable

from rich.highlighter import Highlighter
from textual import events
from textual import widgets
from textual.suggester import Suggester
from textual.types import InputValidationOn
from textual.validation import Validator
from typing_extensions import Literal

from .._extensions import Callbacks
from .._extensions import WidgetExtension

InputType = Literal["integer", "number", "text"]


class TextInput(widgets.Input, WidgetExtension):
    """An extended text input widget.

    Renamed from "Input" to avoid conflicts with callback dependency types.
    """

    def __init__(  # pylint: disable=too-many-arguments,too-many-locals
        self,
        value: str | None = None,
        placeholder: str = "",
        highlighter: Highlighter | None = None,
        password: bool = False,
        *,
        restrict: str | None = None,
        type: InputType = "text",
        max_length: int = 0,
        suggester: Suggester | None = None,
        validators: Validator | Iterable[Validator] | None = None,
        validate_on: Iterable[InputValidationOn] | None = None,
        valid_empty: bool = False,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        styles: dict[str, Any] | None = None,
        disabled_messages: Iterable[type[events.Message]] | None = None,
        callbacks: Callbacks | None = None,
    ) -> None:
        """Initialize the text input widget.

        Args:
            value: An optional default value for the input.
            placeholder: Optional placeholder text for the input.
            highlighter: An optional highlighter for the input.
            password: Flag to say if the field should obfuscate its content.
            restrict: A regex to restrict character inputs.
            type: The type of the input.
            max_length: The maximum length of the input, or 0 for no maximum length.
            suggester: Suggester associated with this input instance.
            validators: An iterable of validators that the Input value will be checked against.
            validate_on: Zero or more of the values "blur", "changed", and "submitted",
                which determine when to do input validation. The default is to do
                validation for all messages.
            valid_empty: Empty values are valid.
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
            restrict=restrict,
            type=type,
            max_length=max_length,
            suggester=suggester,
            validators=validators,
            validate_on=validate_on,
            valid_empty=valid_empty,
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
