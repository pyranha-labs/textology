"""Extended Textual widget that is an item within a ListView, and contains metadata about the selection."""

from typing import Any
from typing import Iterable

from textual import events
from textual import widgets
from textual.widget import Widget

from ._extensions import Callbacks
from ._extensions import WidgetExtension
from ._textual._label import Label


class ListItem(widgets.ListItem, WidgetExtension):
    """An extended widget that is an item within a ListView, and contains metadata about the selection."""

    # Recommended events to ignore when widgets are used in ListViews to prevent large unneeded event batches.
    default_disabled_messages = (
        events.Mount,
        events.Unmount,
        events.Show,
        events.Hide,
        events.Resize,
    )

    def __init__(
        self,
        *children: Widget,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        data: Any = None,
        styles: dict[str, Any] | None = None,
        disabled_messages: Iterable[type[events.Message]] | None = None,
        callbacks: Callbacks | None = None,
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
            styles: Local inline styles to apply on top of the class' styles for only this instance.
            disabled_messages: List of messages to disable on this widget instance only.
            callbacks: Mapping of callbacks to send messages to instead of sending to default handler.
        """
        if not children:
            label = name
            if data and "label" in data:
                label = data["label"]
            if label:
                children = [Label(label, disabled_messages=ListItem.default_disabled_messages)]

        super().__init__(*children, name=name, id=id, classes=classes, disabled=disabled)
        self.__extend_widget__(
            styles=styles,
            disabled_messages=disabled_messages,
            callbacks=callbacks,
        )
        self.data = data
        self.menu_index: int | None = None
