"""Extended Textual RadioSet widget."""

from typing import Any

from textual import widgets

from .._extensions import WidgetExtension


class RadioSet(WidgetExtension, widgets.RadioSet):
    """Widget for grouping a collection of radio buttons into a set."""

    def __init__(
        self,
        *buttons: str | widgets.RadioButton,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        **extension_configs: Any,
    ) -> None:
        """Initialize the radio set.

        Args:
            buttons: A collection of labels or "RadioButton"(s) to group together.
            name: The name of the radio set.
            id: The ID of the radio set in the DOM.
            classes: The CSS classes of the radio set.
            disabled: Whether the radio set is disabled or not.
            extension_configs: Widget extension configurations, such as dynamically provided local callbacks by name.
        """
        super().__init__(
            *buttons,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self.__extend_widget__(**extension_configs)
