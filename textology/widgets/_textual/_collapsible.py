"""Extended Textual Collapsible widget."""

from typing import Any
from typing import Iterable

from textual import events
from textual import widgets
from textual.widget import Widget

from .._extensions import Callbacks
from .._extensions import WidgetExtension


class Collapsible(widgets.Collapsible, WidgetExtension):
    """An extended collapsible container."""

    def __init__(  # pylint: disable=too-many-arguments
        self,
        *children: Widget,
        title: str = "Toggle",
        collapsed: bool = True,
        collapsed_symbol: str = "▶",
        expanded_symbol: str = "▼",
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        styles: dict[str, Any] | None = None,
        disabled_messages: Iterable[type[events.Message]] | None = None,
        callbacks: Callbacks | None = None,
    ) -> None:
        """Initialize the collapsible widget.

        Args:
            *children: Contents that will be collapsed/expanded.
            title: Title of the collapsed/expanded contents.
            collapsed: Default status of the contents.
            collapsed_symbol: Collapsed symbol before the title.
            expanded_symbol: Expanded symbol before the title.
            name: The name of the collapsible.
            id: The ID of the widget in the DOM.
            classes: The CSS classes of the widget.
            disabled: Whether the widget is disabled or not.
            styles: Local inline styles to apply on top of the class' styles for only this instance.
            disabled_messages: List of messages to disable on this widget instance only.
            callbacks: Mapping of callbacks to send messages to instead of sending to default handler.
        """
        super().__init__(
            *children,
            title=title,
            collapsed=collapsed,
            collapsed_symbol=collapsed_symbol,
            expanded_symbol=expanded_symbol,
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
