"""Extended Textual Tree widget."""

from typing import Any
from typing import Iterable

from rich.text import TextType
from textual import events
from textual import widgets
from textual.widgets.tree import TreeDataType

from .._extensions import Callbacks
from .._extensions import WidgetExtension


class Tree(widgets.Tree, WidgetExtension):  # pylint: disable=too-many-ancestors
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
        styles: dict[str, Any] | None = None,
        disabled_messages: Iterable[type[events.Message]] | None = None,
        callbacks: Callbacks | None = None,
    ) -> None:
        """Initialize a Tree.

        Args:
            label: The label of the root node of the tree.
            data: The optional data to associate with the root node of the tree.
            name: The name of the Tree.
            id: The ID of the tree in the DOM.
            classes: The CSS classes of the tree.
            disabled: Whether the tree is disabled or not.
            styles: Local inline styles to apply on top of the class' styles for only this instance.
            disabled_messages: List of messages to disable on this widget instance only.
            callbacks: Mapping of callbacks to send messages to instead of sending to default handler.
        """
        super().__init__(
            label=label,
            data=data,
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
