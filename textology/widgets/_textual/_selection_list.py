"""Extended Textual SelectionList widget."""

from typing import Any

from rich.text import TextType
from textual import widgets
from textual.widgets._selection_list import Selection
from textual.widgets._selection_list import SelectionType

from .._extensions import WidgetExtension


class SelectionList(WidgetExtension, widgets.SelectionList):  # pylint: disable=too-many-ancestors
    """An extended vertical selection list that allows making multiple selections."""

    def __init__(
        self,
        *selections: Selection | tuple[TextType, SelectionType] | tuple[TextType, SelectionType, bool],
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        **extension_configs: Any,
    ) -> None:
        """Initialize the selection list.

        Args:
            *selections: The content for the selection list.
            name: The name of the selection list.
            id: The ID of the selection list in the DOM.
            classes: The CSS classes of the selection list.
            disabled: Whether the selection list is disabled or not.
            extension_configs: Widget extension configurations, such as dynamically provided local callbacks by name.
        """
        super().__init__(
            *selections,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self.__extend_widget__(**extension_configs)
