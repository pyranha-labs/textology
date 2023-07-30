"""Extended Textual Pretty widget."""

from typing import Any

from textual import widgets

from .._extensions import WidgetExtension


class Pretty(WidgetExtension, widgets.Pretty):
    """An extended pretty-printing widget."""

    DEFAULT_CSS = """
    Pretty {
        height: auto;
    }
    """

    def __init__(
        self,
        obj: Any,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        **extension_configs: Any,
    ) -> None:
        """Initialize the Pretty widget.

        Args:
            obj: The object to pretty-print.
            name: The name of the pretty widget.
            id: The ID of the pretty in the DOM.
            classes: The CSS classes of the pretty.
            extension_configs: Widget extension configurations, such as dynamically provided local callbacks by name.
        """
        super().__init__(
            object=obj,
            name=name,
            id=id,
            classes=classes,
        )
        self.__extend_widget__(**extension_configs)
