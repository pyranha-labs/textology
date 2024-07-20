"""Widget metadata that is used to create an item within a ListView on demand."""

from typing import Any
from typing import Iterable

from textual import events

from ._extensions import Callbacks
from ._list_item import ListItem


class ListItemMeta:
    """A metadata class used to create, and recreate, list items that will be used in list views."""

    def __init__(  # pylint: disable=too-many-arguments
        self,
        item_type: type[ListItem] = ListItem,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        data: Any = None,
        styles: dict[str, Any] | None = None,
        disabled_messages: Iterable[type[events.Message]] | None = None,
        callbacks: Callbacks | None = None,
    ) -> None:
        """Initialize metadata object to allow creating list items on demand.

        Args:
            item_type: Type of list item to instantiate with the metadata values.
            name: The name of the widget.
            id: The ID of the widget in the DOM.
            classes: The CSS classes for the widget.
            disabled: Whether the widget is disabled or not.
            data: Optional data associated with the list item.
                If no child is provided for display, the data will be searched for a "label" key to use in a Label.
            styles: Local inline styles to apply on top of the class' styles for only this instance.
            disabled_messages: List of messages to disable on this widget instance only.
            callbacks: Mapping of callbacks to send messages to instead of sending to default handler.
        """
        if not issubclass(item_type, ListItem):
            raise ValueError("Item type must be a subclass of ListItem")
        self.item_type = item_type
        self.name = name
        self.id = id
        self.classes = classes
        self.disabled = disabled
        self.data = data
        self.menu_index: int | None = None
        self.extension_configs = {
            "styles": styles,
            "disabled_messages": disabled_messages,
            "callbacks": callbacks,
        }

    def to_item(self) -> ListItem:
        """Create the underlying list item widget.

        Returns:
            Newly created item that can be used in a list view.
        """
        item = self.item_type(
            name=self.name,
            id=self.id,
            classes=self.classes,
            disabled=self.disabled,
            data=self.data,
            **self.extension_configs,
        )
        item.menu_index = self.menu_index
        return item
