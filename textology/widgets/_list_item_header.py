"""List item that acts as an unselectable header between groups."""

from typing import Any
from typing import Iterable

from textual import events
from textual.widget import Widget

from ._extensions import Callbacks
from ._list_item import ListItem


class ListItemHeader(ListItem):
    """A widget that is an item within a ListView that acts as an unselectable header between list items."""

    DEFAULT_CSS = """
    ListItemHeader>Widget {
        color: $text;
        text-style: bold;
    }
    ListItemHeader:hover>Widget {
        color: $text;
        text-style: bold;
    }
    """

    def __init__(
        self,
        *children: Widget,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        disable_click: bool = True,
        data: Any = None,
        styles: dict[str, Any] | None = None,
        disabled_messages: Iterable[type[events.Message]] | None = None,
        callbacks: Callbacks | None = None,
    ) -> None:
        """Initialize a ListItemHeader with extension arguments.

        Args:
            *children: Child widgets.
            name: The name of the widget.
            id: The ID of the widget in the DOM.
            classes: The CSS classes for the widget.
            disabled: Whether the widget is disabled or not.
            disable_click: Whether clicking the widget it disabled.
            data: Optional data associated with the list item.
                If no child is provided for display, the data will be searched for a "label" key to use in a Label.
            styles: Local inline styles to apply on top of the class' styles for only this instance.
            disabled_messages: List of messages to disable on this widget instance only.
            callbacks: Mapping of callbacks to send messages to instead of sending to default handler.
        """
        super().__init__(
            *children,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
            data=data,
            styles=styles,
            disabled_messages=disabled_messages,
            callbacks=callbacks,
        )
        self.disable_click = disable_click

    async def _on_click(self, event: events.Click) -> None:
        """Disable clicking header items."""
        if self.disable_click:
            event.stop()
            event.prevent_default()
