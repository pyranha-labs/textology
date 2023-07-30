"""Extended Textual Tab widgets."""

from typing import Any

from rich.text import TextType
from textual import widgets

from .._extensions import WidgetExtension


class Tab(WidgetExtension, widgets.Tab):
    """An extended widget to manage a single tab within a Tabs widget."""

    def __init__(
        self,
        label: TextType,
        *,
        id: str | None = None,
        classes: str | None = None,
        **extension_configs: Any,
    ) -> None:
        """Initialize a Tab.

        Args:
            label: The label to use in the tab.
            id: Optional ID for the widget.
            classes: Space separated list of class names.
            extension_configs: Widget extension configurations, such as dynamically provided local callbacks by name.
        """
        super().__init__(
            label,
            id=id,
            classes=classes,
        )
        self.__extend_widget__(**extension_configs)


class Tabs(WidgetExtension, widgets.Tabs):
    """An extended row of tabs."""

    def __init__(
        self,
        *tabs: Tab | TextType,
        active: str | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        **extension_configs: Any,
    ) -> None:
        """Initialize a Tabs widget.

        Args:
            *tabs: Positional argument should be explicit Tab objects, or a str or Text.
            active: ID of the tab which should be active on start.
            name: Optional name for the input widget.
            id: Optional ID for the widget.
            classes: Optional initial classes for the widget.
            disabled: Whether the input is disabled or not.
            extension_configs: Widget extension configurations, such as dynamically provided local callbacks by name.
        """
        super().__init__(
            *tabs,
            active=active,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self.__extend_widget__(**extension_configs)
