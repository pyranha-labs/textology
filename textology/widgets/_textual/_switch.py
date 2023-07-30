"""Extended Textual Switch widget."""

from typing import Any

from textual import widgets

from .._extensions import WidgetExtension


class Switch(WidgetExtension, widgets.Switch):
    """An extended switch widget that represents a boolean value."""

    def __init__(
        self,
        value: bool = False,
        *,
        animate: bool = True,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        **extension_configs: Any,
    ) -> None:
        """Initialize the switch.

        Args:
            value: The initial value of the switch.
            animate: True if the switch should animate when toggled.
            name: The name of the switch.
            id: The ID of the switch in the DOM.
            classes: The CSS classes of the switch.
            disabled: Whether the switch is disabled or not.
            extension_configs: Widget extension configurations, such as dynamically provided local callbacks by name.
        """
        super().__init__(
            value,
            animate=animate,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self.__extend_widget__(**extension_configs)
