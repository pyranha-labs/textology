"""Collection of new, and extended, Textual widgets.

"Extended" Textual widgets strive to maintain 100% parity with their basic counterpart for all standard arguments,
such as id/children/etc. This is to ensure they can all be directly dropped into existing Textual applications, before
any extension functionality is used. All Textual basic widgets should be 100% forward compatible with Textology widgets,
and all Textology widgets should be 100% backwards compatible with Textual widgets, in settings where no extended
functionality is being used.

This file must be kept in sync with the __init__.pyi's import list.
The pyi file is used by text editors and type checkers to see the lazily loaded classes.
"""

import typing
from importlib import import_module

from ._extensions import Widget

# Lazily load widgets to decrease startup time and allow multi version support.
if typing.TYPE_CHECKING:  # pragma: no cover. Exclude from coverage to allow lazy imports without import errors.
    from ._button import Button
    from ._button import SelectButton
    from ._extensions import Callback
    from ._extensions import Callbacks
    from ._extensions import Clickable
    from ._extensions import Static
    from ._extensions import ToggleButton
    from ._extensions import WidgetExtension
    from ._extensions import walk_all_children
    from ._horizontal_menus import HorizontalMenus
    from ._list_item import ListItem
    from ._list_item_header import ListItemHeader
    from ._list_item_meta import ListItemMeta
    from ._list_view import ListView
    from ._location import Location
    from ._modal_dialog import ModalDialog
    from ._multi_select import MultiSelect
    from ._page_container import PageContainer
    from ._popup_text import PopupText
    from ._store import Store
    from ._text import Text
    from ._textual._checkbox import Checkbox
    from ._textual._collapsible import Collapsible
    from ._textual._containers import Center
    from ._textual._containers import Container
    from ._textual._containers import Grid
    from ._textual._containers import Horizontal
    from ._textual._containers import HorizontalScroll
    from ._textual._containers import Middle
    from ._textual._containers import ScrollableContainer
    from ._textual._containers import Vertical
    from ._textual._containers import VerticalScroll
    from ._textual._content_switcher import ContentSwitcher
    from ._textual._data_table import DataTable
    from ._textual._digits import Digits
    from ._textual._directory_tree import DirectoryTree
    from ._textual._footer import Footer
    from ._textual._header import Header
    from ._textual._label import Label
    from ._textual._loading_indicator import LoadingIndicator
    from ._textual._log import Log
    from ._textual._markdown import Markdown
    from ._textual._markdown import MarkdownViewer
    from ._textual._option_list import OptionList
    from ._textual._pretty import Pretty
    from ._textual._progress_bar import ProgressBar
    from ._textual._radio_button import RadioButton
    from ._textual._radio_set import RadioSet
    from ._textual._rich_log import RichLog
    from ._textual._rule import Rule
    from ._textual._select import Select
    from ._textual._selection_list import SelectionList
    from ._textual._sparkline import Sparkline
    from ._textual._switch import Switch
    from ._textual._tabbed_content import TabbedContent
    from ._textual._tabbed_content import TabPane
    from ._textual._tabs import Tab
    from ._textual._tabs import Tabs
    from ._textual._text_area import TextArea
    from ._textual._text_input import TextInput
    from ._textual._tooltip import Tooltip
    from ._textual._tree import Tree
    from ._tree import LazyTree

_module_cache: dict[str, type[Widget]] = {
    "Widget": Widget,
}
_module_map = {
    "Button": "._button",
    "Callback": "._extensions",
    "Callbacks": "._extensions",
    "Center": "._textual._containers",
    "Checkbox": "._textual._checkbox",
    "Clickable": "._extensions",
    "Collapsible": "._textual._collapsible",
    "Container": "._textual._containers",
    "ContentSwitcher": "._textual._content_switcher",
    "DataTable": "._textual._data_table",
    "Digits": "._textual._digits",
    "DirectoryTree": "._textual._directory_tree",
    "Footer": "._textual._footer",
    "Grid": "._textual._containers",
    "Header": "._textual._header",
    "Horizontal": "._textual._containers",
    "HorizontalMenus": "._horizontal_menus",
    "HorizontalScroll": "._textual._containers",
    "LazyTree": "._tree",
    "Label": "._textual._label",
    "ListItem": "._list_item",
    "ListItemHeader": "._list_item_header",
    "ListItemMeta": "._list_item_meta",
    "ListView": "._list_view",
    "LoadingIndicator": "._textual._loading_indicator",
    "Location": "._location",
    "Log": "._textual._log",
    "Markdown": "._textual._markdown",
    "MarkdownViewer": "._textual._markdown",
    "Middle": "._textual._containers",
    "ModalDialog": "._modal_dialog",
    "MultiSelect": "._multi_select",
    "OptionList": "._textual._option_list",
    "PageContainer": "._page_container",
    "PopupText": "._popup_text",
    "Pretty": "._textual._pretty",
    "ProgressBar": "._textual._progress_bar",
    "RadioButton": "._textual._radio_button",
    "RadioSet": "._textual._radio_set",
    "RichLog": "._textual._rich_log",
    "Rule": "._textual._rule",
    "ScrollableContainer": "._textual._containers",
    "Select": "._textual._select",
    "SelectButton": "._button",
    "SelectionList": "._textual._selection_list",
    "Sparkline": "._textual._sparkline",
    "Static": "._extensions",
    "StaticFactory": "._extensions",
    "Store": "._store",
    "Switch": "._textual._switch",
    "Tab": "._textual._tabs",
    "TabbedContent": "._textual._tabbed_content",
    "Tabs": "._textual._tabs",
    "TabPane": "._textual._tabbed_content",
    "Text": "._text",
    "TextArea": "._textual._text_area",
    "TextInput": "._textual._text_input",
    "ToggleButtonFactory": "._extensions",
    "Tooltip": "._textual._tooltip",
    "Tree": "._textual._tree",
    "Vertical": "._textual._containers",
    "VerticalScroll": "._textual._containers",
    "WidgetExtension": "._extensions",
    "WidgetFactory": "._extensions",
    "walk_all_children": "._extensions",
}
__all__ = tuple(_module_cache.keys()) + tuple(_module_map.keys())


def __getattr__(attr_name: str) -> typing.Any:
    """Lazily load widgets, functions, and constants to decrease startup time."""
    try:
        return _module_cache[attr_name]
    except KeyError:
        pass

    if attr_name not in __all__:
        raise AttributeError(f"module 'textology.widgets' has no attribute '{attr_name}'")

    widget_module_path = _module_map.get(attr_name)
    module = import_module(widget_module_path, package="textology.widgets")
    attr = getattr(module, attr_name)
    _module_cache[attr_name] = attr
    return attr
