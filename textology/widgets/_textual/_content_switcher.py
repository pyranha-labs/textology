"""Extended Textual ContentSwitcher widget."""

from typing import Any
from typing import Iterable

from textual import events
from textual import widgets
from textual.widget import Widget

from .._extensions import Callbacks
from .._extensions import WidgetExtension


class ContentSwitcher(widgets.ContentSwitcher, WidgetExtension):
    """An extended widget for switching between different children.

    Note:
        All child widgets that are to be switched between need a unique ID.
        Children that have no ID will be hidden and ignored.
    """

    def __init__(
        self,
        *children: Widget,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        initial: str | None = None,
        styles: dict[str, Any] | None = None,
        disabled_messages: Iterable[type[events.Message]] | None = None,
        callbacks: Callbacks | None = None,
    ) -> None:
        """Initialize the content switching widget.

        Args:
            *children: The widgets to switch between.
            name: The name of the content switcher.
            id: The ID of the content switcher in the DOM.
            classes: The CSS classes of the content switcher.
            disabled: Whether the content switcher is disabled or not.
            initial: The ID of the initial widget to show, ``None`` or empty string for the first tab.
            styles: Local inline styles to apply on top of the class' styles for only this instance.
            disabled_messages: List of messages to disable on this widget instance only.
            callbacks: Mapping of callbacks to send messages to instead of sending to default handler.

        Note:
            If `initial` is not supplied, no children will be shown to start with.
        """
        super().__init__(*children, name=name, id=id, classes=classes, disabled=disabled, initial=initial)
        self.__extend_widget__(
            styles=styles,
            disabled_messages=disabled_messages,
            callbacks=callbacks,
        )

    def next_child(self) -> str | None:
        """Find the next child available in the content list.

        Returns:
            The id of the next child if not currently displaying last, None otherwise.
        """
        next_child = None
        children = [child.id for child in self.children if child.id]
        if self.current != children[-1]:
            current_index = children.index(self.current)
            next_child = children[current_index + 1]
        return next_child

    def previous_child(self) -> str | None:
        """Find the previous child available in the content list.

        Returns:
            The id of the previous child if not currently displaying first, None otherwise.
        """
        previous_child = None
        children = [child.id for child in self.children if child.id]
        if self.current != children[0]:
            current_index = children.index(self.current)
            previous_child = children[current_index - 1]
        return previous_child

    def switch_to_next(self) -> str | None:
        """Find and switch to the last child available in the content list.

        Returns:
            The id of the new child if not currently displaying last, None otherwise.
        """
        next_child = self.next_child()
        if next_child:
            self.current = next_child
        return next_child

    def switch_to_previous(self) -> str | None:
        """Find and switch to the previous child available in the content list.

        Returns:
            The id of the new child if not currently displaying first, None otherwise.
        """
        previous_child = self.previous_child()
        if previous_child:
            self.current = previous_child
        return previous_child
