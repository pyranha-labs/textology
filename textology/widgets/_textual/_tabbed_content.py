"""Extended Textual Tab Content widgets."""

from typing import Any

from rich.text import TextType
from textual import widgets
from textual.widget import Widget

from .._extensions import WidgetExtension


class TabbedContent(WidgetExtension, widgets.TabbedContent):
    """An extended container with associated tabs to toggle content visibility."""

    def __init__(
        self,
        *titles: TextType,
        initial: str = "",
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        **extension_configs: Any,
    ) -> None:
        """Initialize a TabbedContent widgets.

        Args:
            *titles: Positional argument will be used as title.
            initial: The id of the initial tab, or empty string to select the first tab.
            name: The name of the button.
            id: The ID of the button in the DOM.
            classes: The CSS classes of the button.
            disabled: Whether the button is disabled or not.
            extension_configs: Widget extension configurations, such as dynamically provided local callbacks by name.
        """
        super().__init__(
            *titles,
            initial=initial,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self.__extend_widget__(**extension_configs)


class TabPane(WidgetExtension, widgets.TabPane):
    """An extended container for switchable content, with additional title."""

    def __init__(
        self,
        title: TextType,
        *children: Widget,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        **extension_configs: Any,
    ) -> None:
        """Initialize a TabPane.

        Args:
            title: Title of the TabPane (will be displayed in a tab label).
            *children: Widget to go inside the TabPane.
            name: Optional name for the TabPane.
            id: Optional ID for the TabPane.
            classes: Optional initial classes for the widget.
            disabled: Whether the TabPane is disabled or not.
            extension_configs: Widget extension configurations, such as dynamically provided local callbacks by name.
        """
        super().__init__(
            title,
            *children,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self.__extend_widget__(**extension_configs)
