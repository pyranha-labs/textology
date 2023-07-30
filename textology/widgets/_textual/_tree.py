"""Extended Textual Tree widget."""

from typing import Any

from rich.text import TextType
from textual import widgets
from textual.widgets._tree import TreeDataType

from .._extensions import WidgetExtension


class Tree(WidgetExtension, widgets.Tree):  # pylint: disable=too-many-ancestors
    """An extended widget for displaying and navigating data in a tree."""

    def __init__(
        self,
        label: TextType,
        data: TreeDataType | None = None,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        **extension_configs: Any,
    ) -> None:
        """Initialize a Tree.

        Args:
            label: The label of the root node of the tree.
            data: The optional data to associate with the root node of the tree.
            name: The name of the Tree.
            id: The ID of the tree in the DOM.
            classes: The CSS classes of the tree.
            disabled: Whether the tree is disabled or not.
            extension_configs: Widget extension configurations, such as dynamically provided local callbacks by name.
        """
        super().__init__(
            label=label,
            data=data,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self.__extend_widget__(**extension_configs)
