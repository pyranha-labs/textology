"""List item that acts as an unselectable header between groups."""

from typing import Any

from textual.events import Click
from textual.widget import Widget

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
        **extension_configs: Any,
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
            extension_configs: Widget extension configurations, such as dynamically provided local callbacks by name.
        """
        super().__init__(
            *children,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
            data=data,
            **extension_configs,
        )
        self.disable_click = disable_click

    async def _on_click(self, event: Click) -> None:
        """Disable clicking header items."""
        if self.disable_click:
            event.stop()
            event.prevent_default()
