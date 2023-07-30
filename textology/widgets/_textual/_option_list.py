"""Extended Textual OptionList widget."""

from typing import Any

from textual import widgets
from textual.widgets._option_list import NewOptionListContent

from .._extensions import WidgetExtension


class OptionList(WidgetExtension, widgets.OptionList):
    """An extended vertical option list with bounce-bar highlighting."""

    def __init__(
        self,
        *content: NewOptionListContent,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        **extension_configs: Any,
    ) -> None:
        """Initialize the option list.

        Args:
            *content: The content for the option list.
            name: The name of the option list.
            id: The ID of the option list in the DOM.
            classes: The CSS classes of the option list.
            disabled: Whether the option list is disabled or not.
            extension_configs: Widget extension configurations, such as dynamically provided local callbacks by name.
        """
        super().__init__(
            *content,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self.__extend_widget__(**extension_configs)
