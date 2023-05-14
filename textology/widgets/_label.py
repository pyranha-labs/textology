"""Extended Textual label widget for displaying text-oriented renderables."""

from typing import Any

from rich.console import RenderableType
from textual import widgets

from ._extensions import WidgetExtension


class Label(WidgetExtension, widgets.Label):
    """An extended, simple, label widget for displaying text-oriented renderables."""

    def __init__(
        self,
        renderable: RenderableType = "",
        *,
        expand: bool = False,
        shrink: bool = False,
        markup: bool = True,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        **extension_configs: Any,
    ) -> None:
        """Initialize a Label widget with extension arguments.

        Args:
            renderable: A Rich renderable, or string containing console markup.
            expand: Expand content if required to fill container.
            shrink: Shrink content if required to fill container.
            markup: True if markup should be parsed and rendered.
            name: Name of widget.
            id: ID of Widget.
            classes: Space separated list of class names.
            disabled: Whether the static is disabled or not.
            extension_configs: Widget extension configurations, such as dynamically provided local callbacks by name.
        """
        super().__init__(
            renderable,
            expand=expand,
            shrink=shrink,
            markup=markup,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self.__extend_widget__(**extension_configs)
