"""Extended Textual OptionList widget."""

from typing import Any
from typing import Iterable

from textual import events
from textual import widgets
from textual.widgets._option_list import NewOptionListContent

from .._extensions import Callbacks
from .._extensions import WidgetExtension


class OptionList(widgets.OptionList, WidgetExtension):
    """An extended vertical option list with bounce-bar highlighting."""

    def __init__(
        self,
        *content: NewOptionListContent,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        styles: dict[str, Any] | None = None,
        disabled_messages: Iterable[type[events.Message]] | None = None,
        callbacks: Callbacks | None = None,
    ) -> None:
        """Initialize the option list.

        Args:
            *content: The content for the option list.
            name: The name of the option list.
            id: The ID of the option list in the DOM.
            classes: The CSS classes of the option list.
            disabled: Whether the option list is disabled or not.
            styles: Local inline styles to apply on top of the class' styles for only this instance.
            disabled_messages: List of messages to disable on this widget instance only.
            callbacks: Mapping of callbacks to send messages to instead of sending to default handler.
        """
        super().__init__(
            *content,
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
