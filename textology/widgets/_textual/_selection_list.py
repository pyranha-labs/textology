"""Extended Textual SelectionList widget."""

from typing import Any
from typing import Iterable

from rich.text import TextType
from textual import events
from textual import widgets
from textual.widgets._selection_list import Selection
from textual.widgets._selection_list import SelectionType

from .._extensions import Callbacks
from .._extensions import WidgetExtension


class SelectionList(widgets.SelectionList, WidgetExtension):  # pylint: disable=too-many-ancestors
    """An extended vertical selection list that allows making multiple selections."""

    def __init__(
        self,
        *selections: Selection | tuple[TextType, SelectionType] | tuple[TextType, SelectionType, bool],
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        styles: dict[str, Any] | None = None,
        disabled_messages: Iterable[type[events.Message]] | None = None,
        callbacks: Callbacks | None = None,
    ) -> None:
        """Initialize the selection list.

        Args:
            *selections: The content for the selection list.
            name: The name of the selection list.
            id: The ID of the selection list in the DOM.
            classes: The CSS classes of the selection list.
            disabled: Whether the selection list is disabled or not.
            styles: Local inline styles to apply on top of the class' styles for only this instance.
            disabled_messages: List of messages to disable on this widget instance only.
            callbacks: Mapping of callbacks to send messages to instead of sending to default handler.
        """
        super().__init__(
            *selections,
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
