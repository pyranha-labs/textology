"""Extended Textual, simple, clickable, button."""

from typing import Any

from rich.text import TextType
from textual import widgets
from textual.message import Message
from textual.widgets.button import ButtonVariant

from ._extensions import Clickable
from ._extensions import WidgetExtension


class Button(Clickable, WidgetExtension, widgets.Button):
    """An extended, simple, clickable button."""

    def __init__(
        self,
        label: TextType | None = None,
        variant: ButtonVariant = "default",
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        **extension_configs: Any,
    ) -> None:
        """Initialize a Button widget with extension arguments.

        Args:
            label: The text that appears within the button.
            variant: The variant of the button.
            name: The name of the button.
            id: The ID of the button in the DOM.
            classes: The CSS classes of the button.
            disabled: Whether the button is disabled or not.
            extension_configs: Widget extension configurations, such as dynamically provided local callbacks by name.
        """
        super().__init__(
            label=label,
            variant=variant,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self.__extend_widget__(**extension_configs)

    async def intercept_message(self, message: Message) -> Message | None:
        """Update reactive attributes on press."""
        if isinstance(message, Button.Pressed):
            self.update_n_clicks()
        return message
