"""Extended Textual ContentSwitcher widget."""

from typing import Any

from textual import widgets
from textual.widget import Widget

from .._extensions import WidgetExtension


class ContentSwitcher(WidgetExtension, widgets.ContentSwitcher):
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
        **extension_configs: Any,
    ) -> None:
        """Initialize the content switching widget.

        Args:
            *children: The widgets to switch between.
            name: The name of the content switcher.
            id: The ID of the content switcher in the DOM.
            classes: The CSS classes of the content switcher.
            disabled: Whether the content switcher is disabled or not.
            initial: The ID of the initial widget to show, ``None`` or empty string for the first tab.
            extension_configs: Widget extension configurations, such as dynamically provided local callbacks by name.

        Note:
            If `initial` is not supplied, no children will be shown to start with.
        """
        super().__init__(*children, name=name, id=id, classes=classes, disabled=disabled, initial=initial)
        self.__extend_widget__(**extension_configs)
