"""Extended Textual, simple, clickable, button."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any
from typing import Iterable

from rich.text import Text
from rich.text import TextType
from textual import events
from textual import widgets
from textual.message import Message
from textual.pad import HorizontalPad
from textual.reactive import reactive
from textual.widgets.button import ButtonVariant
from typing_extensions import override

from ._extensions import Callbacks
from ._extensions import Clickable
from ._extensions import WidgetExtension

if TYPE_CHECKING:
    from textual.app import RenderResult


class Button(widgets.Button, WidgetExtension, Clickable):
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
        styles: dict[str, Any] | None = None,
        disabled_messages: Iterable[type[events.Message]] | None = None,
        callbacks: Callbacks | None = None,
    ) -> None:
        """Initialize a Button widget with extension arguments.

        Args:
            label: The text that appears within the button.
            variant: The variant of the button.
            name: The name of the button.
            id: The ID of the button in the DOM.
            classes: The CSS classes of the button.
            disabled: Whether the button is disabled or not.
            styles: Local inline styles to apply on top of the class' styles for only this instance.
            disabled_messages: List of messages to disable on this widget instance only.
            callbacks: Mapping of callbacks to send messages to instead of sending to default handler.
        """
        super().__init__(
            label=label,
            variant=variant,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self.__extend_widget__(
            styles=styles,
            disabled_messages=disabled_messages,
            callbacks=callbacks,
        )

    async def intercept_message(self, message: Message) -> Message | None:
        """Update reactive attributes on press."""
        if isinstance(message, Button.Pressed):
            self.update_n_clicks()
        return message


class SelectButton(Button):
    """A button that tracks whether it is selected or not.

    Differs from RadioButton and ToggleButton in that it has all the same functionality as a Button,
    but also automatically updates and tracks whether it is currently "selected" or not on press events.
    """

    selected: bool = reactive(False, repaint=False, init=False)

    class Selected(Message):
        """Event sent when the button is selected/de-selected."""

        def __init__(self, button: SelectButton, selected: bool) -> None:
            """Initialize the selection update event.

            Args:
                button: The button that sent the event.
                selected: Whether the button is selected.
            """
            super().__init__()
            self.button = button
            self.selected = selected

        @property
        def control(self) -> SelectButton:
            """The button that was selected/deselected."""
            return self.button

    def __init__(
        self,
        label: TextType | None = None,
        *,
        selected: bool = False,
        selected_chars: str = "● ",
        deselected_chars: str = "⭘ ",
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        styles: dict[str, Any] | None = None,
        disabled_messages: Iterable[type[events.Message]] | None = None,
        callbacks: Callbacks | None = None,
    ) -> None:
        """Initialize a SelectButton widget with extension arguments.

        Args:
            label: The text that appears within the button.
            selected: Whether the initial state of the button is selected.
            selected_chars: Character(s) to use as a label prefix when the item is selected.
            deselected_chars: Character(s) to use as a label prefix when the item is deselected.
            name: The name of the button.
            id: The ID of the button in the DOM.
            classes: The CSS classes of the button.
            disabled: Whether the button is disabled or not.
            styles: Local inline styles to apply on top of the class' styles for only this instance.
            disabled_messages: List of messages to disable on this widget instance only.
            callbacks: Mapping of callbacks to send messages to instead of sending to default handler.
        """
        self._selected_chars = Text.from_markup(selected_chars)
        self._deselected_chars = Text.from_markup(deselected_chars)
        super().__init__(
            label=label,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
            styles=styles,
            disabled_messages=disabled_messages,
            callbacks=callbacks,
        )
        self.selected = selected

    async def intercept_message(self, message: Message) -> Message | None:
        """Update reactive attributes on press."""
        if isinstance(message, widgets.Button.Pressed):
            self.selected = not self.selected
        return message

    @override
    def render(self) -> RenderResult:
        label = (self._selected_chars if self.selected else self._deselected_chars) + self.label.copy()
        label.stylize_before(self.rich_style)
        return HorizontalPad(
            label,
            1,
            1,
            self.rich_style,
            self._get_rich_justify() or "center",
        )

    def watch_selected(self, selected: bool) -> None:
        """Monitor selected state to toggle indicator and trigger selection events."""
        self.post_message(self.Selected(self, selected))
        self.refresh()
