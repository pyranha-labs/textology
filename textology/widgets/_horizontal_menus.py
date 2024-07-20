"""Progressive horizontal set of ListViews with tracking for active item and peeking at next menu."""

from __future__ import annotations

from typing import Any
from typing import Callable
from typing import ClassVar
from typing import Iterable

from textual import containers
from textual import events
from textual.await_complete import AwaitComplete
from textual.binding import Binding
from textual.binding import BindingType
from textual.reactive import reactive
from textual.widget import Widget

from ._extensions import Callbacks
from ._extensions import WidgetExtension
from ._extensions import walk_all_children
from ._list_item import ListItem
from ._list_item_header import ListItemHeader
from ._list_item_meta import ListItemMeta
from ._list_view import ListView


class HorizontalMenus(containers.HorizontalScroll, WidgetExtension):
    """Progressive horizontal set of ListViews with tracking for active item(s).

    Compared to a Tree view, horizontal menus provide quick navigation and visibility into nested objects.
    The menus can be quickly focused, selected, etc., with less vertical traversal in large objects.
    "Previewing" the next menu in a set of menus is also allowed.
    """

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("left", "focus_previous", show=False),
        Binding("right", "focus_next", show=False),
    ]

    # Currently focused item across sub-menus.
    focused: ListItem | None = reactive(None, repaint=False, init=False)
    # Current primary item highlighted across sub-menus (right-most).
    highlighted: ListItem | None = reactive(None, repaint=False, init=False)
    # All highlighted items across sub-menus.
    highlights: list[ListItem] = reactive([], repaint=False, init=False)

    class Focused(events.Message, bubble=True):
        """Posted when the focused item changes."""

        def __init__(self, horizontal_menu: HorizontalMenus, item: ListItem | None) -> None:
            """Initialize focused event.

            Args:
                horizontal_menu: Parent menu containing the item.
                item: New item that was focused.
            """
            super().__init__()
            self.horizontal_menu: HorizontalMenus = horizontal_menu
            self.item: ListItem | None = item

        @property
        def control(self) -> HorizontalMenus:
            """The primary controlling widget that contains the focused item, used by "on()" decorator."""
            return self.horizontal_menu

    class Highlighted(events.Message, bubble=True):
        """Posted when the highlighted item changes."""

        def __init__(self, horizontal_menu: HorizontalMenus, item: ListItem | None) -> None:
            """Initialize highlight event.

            Args:
                horizontal_menu: Parent menu containing the item.
                item: New item that was highlighted.
            """
            super().__init__()
            self.horizontal_menu: HorizontalMenus = horizontal_menu
            self.item: ListItem | None = item

        @property
        def control(self) -> HorizontalMenus:
            """The primary controlling widget that contains the highlighted item, used by "on()" decorator."""
            return self.horizontal_menu

    def __init__(
        self,
        *children: Widget | ListItem | ListItemMeta,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        can_focus: bool = False,
        menu_creator: Callable[[int, list[ListItem]], Widget] | None = None,
        styles: dict[str, Any] | None = None,
        disabled_messages: Iterable[type[events.Message]] | None = None,
        callbacks: Callbacks | None = None,
    ) -> None:
        """Initialize horizontal menus.

        Args:
            *children: Initial menus, or menu items, to display.
                Each "menu" widget must contain a ListView, but does not have to be a ListView itself.
                If children are ListItem or ListItemMeta objects, an initial ListView will be made with menu_creator.
            name: The name of the widget.
            id: The ID of the widget in the DOM.
            classes: The CSS classes for the widget.
            disabled: Whether the widget is disabled or not.
            can_focus: Whether the parent widget can be focused, or only the children widgets.
                If enabled, it will take focus after all the nested ListViews, but before the next sibling.
            menu_creator: Called to create new sub-menus when an item with children is highlighted.
            styles: Local inline styles to apply on top of the class' styles for only this instance.
            disabled_messages: List of messages to disable on this widget instance only.
            callbacks: Mapping of callbacks to send messages to instead of sending to default handler.
        """
        self.menu_creator = menu_creator or self._default_menu_creator
        if any(isinstance(child, (ListItem, ListItemMeta)) for child in children):
            if not all(isinstance(child, (ListItem, ListItemMeta)) for child in children):
                raise ValueError("All initial children must be of same type: ListItem, ListItemMeta, or ListView")
            self._update_menu_index(children, 0)
            children = [
                self.menu_creator(
                    0,
                    [child.to_item() if isinstance(child, ListItemMeta) else child for child in children],
                )
            ]
        super().__init__(
            *children,
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
        self.can_focus = can_focus
        self.menus = []
        for child in children or []:
            menu = None
            if isinstance(child, ListView):
                menu = child
            else:
                for node in walk_all_children(child):
                    if isinstance(node, ListView):
                        menu = node
                        break
            if menu is None:
                raise ValueError("All menu children must contain a ListView widget")
            self.menus.append(menu)

    def action_focus_next(self) -> None:
        """Focus the next widget and ensure the first item is highlighted."""
        self.app.action_focus_next()
        focused = self.app.focused
        if focused in self.menus and focused.index is None and any(focused.children):
            focused.index = 0

    def _add_menu(self, items: list[ListItem]) -> AwaitComplete:
        """Create and add a menu to the list of available menus."""
        new_menu = self.menu_creator(len(self.menus), items)
        mount = None
        if new_menu is not None:
            list_view = None
            if isinstance(new_menu, ListView):
                list_view = new_menu
            else:
                for node in walk_all_children(new_menu):
                    if isinstance(node, ListView):
                        list_view = node
                        break
            if list_view is None:
                raise ValueError("Menus must contain a ListView widget for navigation")
            self.menus.append(list_view)
            mount = self.mount(new_menu)
            await_complete = AwaitComplete(mount)
        else:
            await_complete = AwaitComplete()
        self.call_next(await_complete)
        return await_complete

    @staticmethod
    def _default_menu_creator(menu_index: int, items: list) -> ListView | None:
        """Default menu factory to create submenus when another submenu highlight changes."""
        return (
            ListView(
                *items,
                auto_highlight=False,
                initial_index=None,
                classes=f"--horizontal-menu-{menu_index}",
            )
            if any(not isinstance(item, ListItemHeader) for item in items)
            else None
        )

    def _find_highlighted(self) -> ListItem | None:
        """Find the rightmost highlighted (most recent) item across the menu hierarchy."""
        for menu in reversed(self.menus):
            highlighted = menu.highlighted_child
            if highlighted:
                return highlighted
        return None

    def _find_highlights(self) -> list[ListItem]:
        """Find the highlighted items across all the menus in the hierarchy."""
        highlights = []
        for menu in reversed(self.menus):
            highlighted = menu.highlighted
            if highlighted:
                highlights.append(highlighted)
        return highlights

    def on_descendant_focus(self, focus_event: events.DescendantFocus) -> None:
        """Update highlighted and focused items when focus on nested menus updates."""
        focused = None
        for menu in reversed(self.menus):
            if not menu.has_focus:
                continue
            highlighted_child = menu.highlighted_child
            if highlighted_child:
                self.focused = highlighted_child
                break
        self.focused = focused
        self.highlighted = self._find_highlighted()
        self.highlights = self._find_highlights()
        if not self.highlighted and self.menus and focus_event.widget == self.menus[0]:
            focus_event.widget.index = 0

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        """Update highlighted items and focused menus when highlight on nested item updates."""
        # Ensure ListView with newly highlighted item is focused to ensure no accidental auto highlight on
        # removal of menus > 1 away. Example: Do not auto highlight menu 1 when menu 0 was clicked from menu 2.
        # Auto highlighting occurs in ListView on_focus() to ensure that an item is always selected once focused.
        if event.item and event.item.highlighted:
            self.screen.set_focus(event.list_view)
            self.focused = event.item
            if event.item not in self.highlights:
                self.highlighted = event.item
            self.highlights = self._find_highlights()
        event.stop()
        event.prevent_default()

    def remove_menus(self, last_index: int) -> None:
        """Remove all menus after a specific index.

        Args:
            last_index: Index of the last menu to show.
        """
        for index, child in reversed(list(enumerate(self.children))):
            if index <= last_index:
                continue
            child.remove()
            self.menus.pop(index)

    def show_menu(self, index: int, items: list[ListItem]) -> AwaitComplete:
        """Show a new set of items, either by creating a new menu, or updating an existing menu.

        Args:
            index: Position of the menu to create or update.
            items: New items to show in the menu at the provided index.

        Returns:
            An awaitable object that waits for menus to be added or updated.
        """
        self._update_menu_index(items, index)
        if index >= len(self.menus):
            return self._add_menu(items)
        return self._update_menu(index, items)

    def _update_menu(self, index: int, new_items: list[ListItem]) -> AwaitComplete:
        """Update the items in an existing menu."""
        # Do not count headers towards the available items to display in a sub-menu.
        non_headers = [item for item in new_items if not isinstance(item, ListItemHeader)]
        self.remove_menus(index if non_headers else index - 1)
        if index < len(self.menus):
            awaitable = self.menus[index].replace(new_items)
        else:
            awaitable = AwaitComplete()
            self.call_next(awaitable)
        return awaitable

    @staticmethod
    def _update_menu_index(items: Iterable[ListItem | ListItemMeta], index: int) -> None:
        """Update the menu index value on all items in a list."""
        for item in items:
            item.menu_index = index

    def watch_focused(self, old_value: ListItem | None, new_value: ListItem | None) -> None:
        """Monitor the focused item to update listeners.

        Args:
            old_value: Previously focused list item.
            new_value: Newly focused list item.
        """
        if new_value == old_value or not new_value:
            return
        self.post_message(self.Focused(self, new_value))

    def watch_highlighted(self, old_value: ListItem | None, new_value: ListItem | None) -> None:
        """Monitor the highlighted item to update the submenus and listeners.

        Args:
            old_value: Previously highlighted list item.
            new_value: Newly highlighted list item.
        """
        if new_value == old_value or not new_value:
            return
        menu_items = new_value.data.get("menu_items")
        menu_index = new_value.menu_index or 0
        if menu_items:
            list_items = [item.to_item() for item in menu_items]
            self.show_menu(menu_index + 1, list_items)
        else:
            self.remove_menus(menu_index)
        self.post_message(self.Highlighted(self, new_value))
