"""Progressive horizontal set of ListViews with tracking for active item and peeking at next menu."""

from typing import Any
from typing import Callable

from textual import containers
from textual import events
from textual.reactive import reactive
from textual.widget import Widget

from ._extensions import WidgetExtension
from ._list_item import ListItem
from ._list_item_header import ListItemHeader
from ._list_view import ListView


class HorizontalMenus(WidgetExtension, containers.HorizontalScroll):
    """Progressive horizontal set of ListViews with tracking for active item(s).

    Compared to a Tree view, horizontal menus provide quick navigation and visibility into nested objects.
    The menus can be quickly focused, selected, etc., with less vertical traversal in large objects.
    "Previewing" the next menu in a set of menus is also allowed.
    """

    # Currently focused item across sub-menus.
    focused: ListItem | None = reactive(None, repaint=False, init=False)
    # Current primary item highlighted across sub-menus (right-most).
    highlighted: ListItem | None = reactive(None, repaint=False, init=False)
    # All highlighted items across sub-menus.
    highlights: list[ListItem] = reactive([], repaint=False, init=False)

    def __init__(
        self,
        *children: Widget,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        can_focus: bool = False,
        menu_creator: Callable[[int, list[ListItem]], Widget] = None,
        **extension_configs: Any,
    ) -> None:
        """Initialize horizontal menus.

        Args:
            *children: Initial menus to display.
                Each "menu" widget must contain a ListView, but does not have to be a ListView itself.
            name: The name of the widget.
            id: The ID of the widget in the DOM.
            classes: The CSS classes for the widget.
            disabled: Whether the widget is disabled or not.
            can_focus: Whether the widget can be focused, or only the children.
                If enabled, it will take focus after all the nested ListViews, but before the next sibling.
            menu_creator: Called to create new sub-menus when an item with children is highlighted.
            extension_configs: Widget extension configurations, such as dynamically provided local callbacks by name.
        """
        super().__init__(
            *children,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self.__extend_widget__(**extension_configs)
        self.can_focus = can_focus
        self.menu_creator = menu_creator
        self.menus = []
        for child in children or []:
            menu = None
            if isinstance(child, ListView):
                menu = child
            else:
                for node in child.walk_children():
                    if isinstance(node, ListView):
                        menu = node
                        break
            if not menu:
                raise ValueError("All menu children must contain a ListView widget")
            self.menus.append(menu)

    def _add_menu(self, items: list[ListItem]) -> None:
        """Create and add a menu to the list of available menus."""
        new_menu = self.menu_creator(len(self.menus), items)
        if new_menu:
            self.mount(new_menu)
            list_view = None
            if isinstance(new_menu, ListView):
                list_view = new_menu
            else:
                for node in new_menu.walk_children():
                    if isinstance(node, ListView):
                        list_view = node
                        break
            if not list_view:
                raise ValueError("Menus must contain a ListView widget for navigation")
            self.menus.append(list_view)

    def _find_highlighted(self) -> ListItem:
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

    def on_descendant_focus(self, _: events.DescendantFocus) -> None:
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

    def show_menu(self, index: int, items: list[ListItem]) -> None:
        """Show a new set of items, either by creating a new menu, or updating an existing menu.

        Args:
            index: Position of the menu to create or update.
            items: New items to show in the menu at the provided index.
        """
        if index >= len(self.menus):
            self._add_menu(items)
        else:
            self._update_menu(index, items)

    def _update_menu(self, index: int, new_items: list[ListItem]) -> None:
        """Update the items in an existing menu."""
        # Do not count headers towards the available items to display in a sub-menu.
        non_headers = [item for item in new_items if not isinstance(item, ListItemHeader)]
        self.remove_menus(index if non_headers else index - 1)
        if index < len(self.menus):
            self.menus[index].replace(new_items)
