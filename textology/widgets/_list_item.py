"""Extended Textual widget that is an item within a ListView, and contains metadata about the selection."""

from typing import Any

from textual import events
from textual import widgets
from textual.widget import Widget

from ._extensions import WidgetExtension
from ._textual._label import Label

# Recommended events to ignore when widgets are used in ListViews to prevent large unneeded event batches.
LIST_ITEM_EVENT_IGNORES = (
    events.Mount,
    events.Unmount,
    events.Show,
    events.Hide,
    events.Resize,
)


class ListItem(WidgetExtension, widgets.ListItem):
    """An extended widget that is an item within a ListView, and contains metadata about the selection."""

    def __init__(
        self,
        *children: Widget,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        data: Any = None,
        **extension_configs: Any,
    ) -> None:
        """Initialize a ListItem with extension arguments.

        Args:
            *children: Child widgets.
            name: The name of the widget.
                If no child is provided for display, and no "data" with "label" key, name will be used in a Label.
            id: The ID of the widget in the DOM.
            classes: The CSS classes for the widget.
            disabled: Whether the widget is disabled or not.
            data: Optional data associated with the list item.
                If no child is provided for display, the data will be searched for a "label" key to use in a Label.
            extension_configs: Widget extension configurations, such as dynamically provided local callbacks by name.
        """
        if not children:
            label = name
            if data and "label" in data:
                label = data["label"]
            if label:
                children = [Label(label, disable_messages=LIST_ITEM_EVENT_IGNORES)]

        super().__init__(*children, name=name, id=id, classes=classes, disabled=disabled)
        if "disable_messages" not in extension_configs:
            extension_configs["disable_messages"] = LIST_ITEM_EVENT_IGNORES
        self.__extend_widget__(**extension_configs)
        self.data = data
        self.menu_index: int | None = None
