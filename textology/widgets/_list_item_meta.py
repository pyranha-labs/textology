"""Widget metadata that is used to create an item within a ListView on demand."""

from typing import Any

from ._list_item import ListItem


class ListItemMeta:
    """A metadata class used to create, and recreate, list items that will be used in list views."""

    def __init__(
        self,
        item_type: type[ListItem] = ListItem,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        data: Any = None,
        **extension_configs: Any,
    ) -> None:
        """Initialize metadata object to allow creating list items on demand.

        Args:
            item_type: Type of list item to instantiate with the metadata values.
            name: The name of the widget.
            id: The ID of the widget in the DOM.
            classes: The CSS classes for the widget.
            disabled: Whether the widget is disabled or not.
            data: Optional data associated with the list item.
                If no child is provided for display, the data will be searched for a "name" key to use in a Label.
            extension_configs: Widget extension configurations, such as dynamically provided local callbacks by name.
        """
        if not issubclass(item_type, ListItem):
            raise ValueError("Item type must be a subclass of ListItem")
        self.item_type = item_type
        self.name = name
        self.id = id
        self.classes = classes
        self.data = data
        self.extension_configs = extension_configs
        self.menu_index: int | None = None

    def to_item(self) -> ListItem:
        """Create the underlying list item widget.

        Returns:
            Newly created item that can be used in a list view.
        """
        item = self.item_type(
            name=self.name,
            id=self.id,
            classes=self.classes,
            data=self.data,
            **self.extension_configs,
        )
        item.menu_index = self.menu_index
        return item
