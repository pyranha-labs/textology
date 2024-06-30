"""Extended Textual vertical list view widget."""

from typing import Any
from typing import Iterable

from textual import events
from textual import widgets
from textual.await_complete import AwaitComplete
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import ListItem

from ._extensions import Callback
from ._extensions import WidgetExtension
from ._list_item_header import ListItemHeader


class ListView(widgets.ListView, WidgetExtension):
    """An extended vertical list view widget."""

    default_disabled_messages = [
        # Disable click events, they are already handled by _on_list_item__child_clicked.
        events.Click,
    ]

    # Most recently highlighted item in the list.
    highlighted: ListItem | None = reactive(None, repaint=False, init=False)

    def __init__(
        self,
        *children: ListItem,
        initial_index: int | None = 0,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        auto_highlight: bool = True,
        styles: dict[str, Any] | None = None,
        disabled_messages: Iterable[type[events.Message]] | None = None,
        callbacks: dict[str, Callback] | None = None,
    ) -> None:
        """Initialize a ListView with extension arguments.

        Args:
            *children: The ListItems to display in the list.
            initial_index: The index that should be highlighted when the list is first mounted.
            name: The name of the widget.
            id: The unique ID of the widget used in CSS/query selection.
            classes: The CSS classes of the widget.
            disabled: Whether the ListView is disabled or not.
            auto_highlight: Whether the ListView automatically highlights the first item on focus.
            styles: Local inline styles to apply on top of the class' styles for only this instance.
            disabled_messages: List of messages to disable on this widget instance only.
            callbacks: Mapping of callbacks to send messages to instead of sending to default handler.
        """
        super().__init__(
            *children,
            initial_index=initial_index,
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
        self.auto_highlight = auto_highlight

    def on_focus(self, event: events.Focus) -> None:
        """Automatically highlight the first item in the list when the list is focused."""
        super()._on_focus(event)
        if self.auto_highlight and self.has_focus and self.index is None and self._nodes:
            self.index = 0

    def _on_list_item__child_clicked(
        self,
        event: ListItem._ChildClicked,
    ) -> None:  # pylint: disable=protected-access
        """Stop ListView child click events from propagating past ListView.

        Absorb the event propagation at the ListView level, do not send up the stack, but call default.
        The default operation will send a Selected event that observers can handle.
        """
        # Absorb the event propagation at the ListView level, do not send up the stack, but call default.
        event.stop()
        event.prevent_default()
        super()._on_list_item__child_clicked(event)

    def on_list_view_highlighted(self, _: widgets.ListView.Highlighted) -> None:
        """Update reactive attributes on highlight changes."""
        self.highlighted = self.highlighted_child

    async def _replace(
        self,
        items: list[ListItem],
    ) -> None:
        """Simultaneously swap all the items in the list."""
        # Semantically equivalent to `self.remove_children` + `self.mount`,
        # but reduces refreshes to improve performance.
        self.index = None
        # pylint: disable=protected-access
        to_remove = self.app._detach_from_dom(list(self.children))
        await self.app._prune_nodes(to_remove)
        await self.mount(*items)

    def replace(
        self,
        items: list[ListItem],
    ) -> AwaitComplete:
        """Simultaneously swap all the items in the list.

        Args:
            items: New items to place in the list.

        Returns:
            An awaitable object that waits for items to be mounted.
        """
        await_complete = AwaitComplete(self._replace(items))
        self.call_next(await_complete)
        return await_complete

    def watch_index(self, old_index: int, new_index: int) -> None:
        """Updates the highlighted when the index changes.

        Overrides ListView watch_index to allow support detecting header items that should be skip highlighting.
        """
        if self._is_valid_index(old_index):
            old_child = self._nodes[old_index]
            old_child.highlighted = False

        new_child: Widget | None
        if self._is_valid_index(new_index):
            new_child = self._nodes[new_index]
            if isinstance(new_child, ListItemHeader):
                if new_index == 0:
                    if old_index == 0 or not self._nodes:
                        self.index = None
                    else:
                        self.index = new_index + 1
                else:
                    self.index = new_index + 1 if new_index > old_index else new_index - 1
                return
            new_child.highlighted = True
        else:
            new_child = None

        self._scroll_highlighted_region()
        self.post_message(self.Highlighted(self, new_child))
