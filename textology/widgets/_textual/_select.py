"""Extended Textual Select widget."""

from typing import Any
from typing import Iterable

from textual import widgets
from textual.widgets._select import SelectType

from .._extensions import WidgetExtension


class Select(WidgetExtension, widgets.Select):
    """An extended widget to select from a list of possible options."""

    def __init__(
        self,
        options: Iterable[tuple[str, SelectType]],
        *,
        prompt: str = "Select",
        allow_blank: bool = True,
        value: SelectType | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        **extension_configs: Any,
    ) -> None:
        """Initialize the Select control.

        Args:
            options: Options to select from.
            prompt: Text to show in the control when no option is select.
            allow_blank: Allow the selection of a blank option.
            value: Initial value (should be one of the values in `options`).
            name: The name of the select control.
            id: The ID of the control the DOM.
            classes: The CSS classes of the control.
            disabled: Whether the control is disabled or not.
            extension_configs: Widget extension configurations, such as dynamically provided local callbacks by name.
        """
        super().__init__(
            *options,
            prompt=prompt,
            allow_blank=allow_blank,
            value=value,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self.__extend_widget__(**extension_configs)
