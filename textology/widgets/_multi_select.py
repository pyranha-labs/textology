"""Multiple choice dropdown widget."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any
from typing import Generic
from typing import Iterable

from rich.console import RenderableType
from rich.text import Text
from rich.text import TextType
from textual import events
from textual import on
from textual.css.query import NoMatches
from textual.message import Message
from textual.reactive import var
from textual.types import NoSelection
from textual.types import SelectType
from textual.widgets import Select
from textual.widgets import SelectionList
from textual.widgets._select import SelectCurrent
from textual.widgets.select import EmptySelectError
from textual.widgets.select import InvalidSelectValueError
from textual.widgets.selection_list import Selection
from textual.widgets.selection_list import SelectionType

from ._extensions import Callbacks
from ._textual._containers import Vertical

if TYPE_CHECKING:
    from textual.app import ComposeResult

BLANK = Select.BLANK


class MultiSelectOverlay(SelectionList):  # pylint: disable=too-many-ancestors
    """The 'pop-up' overlay for the MultiSelect control.

    Based off textual.widgets.select.SelectOverlay, but uses SelectionList for multiple choice selection.
    """

    BINDINGS = [
        ("escape", "dismiss"),
        ("backspace,delete", "clear"),
    ]

    DEFAULT_CSS = """
    MultiSelectOverlay {
        border: tall $background;
        background: $panel;
        color: $text;
        width: 100%;
        padding: 0 1;
    }
    MultiSelectOverlay:focus {
        border: tall $background;
    }
    MultiSelectOverlay > .option-list--option {
        padding: 0 1;
    }
    """

    allow_blank: bool = var[bool](False, init=False)

    @dataclass
    class Dismiss(Message):
        """Inform ancestor the overlay should be dismissed."""

        lost_focus: bool = False

    @dataclass
    class UpdateSelection(Message):
        """Inform ancestor the selection changed."""

        selected: list[SelectType]

    def _action_clear(self) -> None:
        """Clear the selected item."""
        self.deselect_all()

    def _action_dismiss(self) -> None:
        """Dismiss the overlay."""
        self.post_message(self.Dismiss())

    def _on_blur(self, _event: events.Blur) -> None:
        """Dismiss the overlay on blur."""
        self.post_message(self.Dismiss(lost_focus=True))

    def _on_selection_list_selected_changed(self, event: SelectionList.SelectedChanged) -> None:
        """Inform parent when an option is selected."""
        event.stop()
        self.post_message(self.UpdateSelection(event.selection_list.selected))

    def _deselect(self, value: SelectionType) -> bool:
        """Mark the given selection as not selected.

        Override default behavior to disable deselection if `allow_blank` is false, and it would deselect last value.
        """
        if len(self.selected) <= 1 and not self.allow_blank:
            return False
        return super()._deselect(value)


class MultiSelect(Generic[SelectType], Vertical, can_focus=True):  # pylint: disable=too-many-ancestors
    """Widget to select multiple choices from a list of possible options.

    A MultiSelect displays the current selection(s) by default. When activated, the widget displays an overlay
    with a list of all possible options.

    Based off textual.widgets.select.Select, but uses SelectionList for multiple choice selection instead of OptionList.
    """

    BINDINGS = [("enter,down,space,up", "show_overlay")]
    DEFAULT_CSS = """
    MultiSelect {
        height: auto;

        & > MultiSelectOverlay {
            width: 1fr;
            display: none;
            height: auto;
            max-height: 12;
            overlay: screen;
            constrain: y;
        }

        &:focus > SelectCurrent {
            border: tall $accent;
        }

        .up-arrow {
            display: none;
        }

        &.-expanded .down-arrow {
            display: none;
        }

        &.-expanded .up-arrow {
            display: block;
        }

        &.-expanded > MultiSelectOverlay {
            display: block;
        }

        &.-expanded > SelectCurrent {
            border: tall $accent;
        }
    }
    """

    expanded: bool = var[bool](False, init=False)
    prompt: str = var[str]("Select", init=False)
    values: list[SelectType] | NoSelection = var[list[SelectType] | NoSelection](BLANK, init=False)

    class Changed(Message):
        """Posted when the selected values change."""

        def __init__(self, select: MultiSelect[SelectType], selected: list[SelectType] | NoSelection) -> None:
            """Initialize the Changed message."""
            super().__init__()
            self.select = select
            self.selected = selected

        @property
        def control(self) -> MultiSelect[SelectType]:
            """The MultiSelect that sent the message."""
            return self.select

    def __init__(
        self,
        options: Iterable[
            Selection[SelectionType] | tuple[TextType, SelectionType] | tuple[TextType, SelectionType, bool]
        ],
        *,
        prompt: str = "Select",
        allow_blank: bool = True,
        values: list[SelectType] | NoSelection = BLANK,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        styles: dict[str, Any] | None = None,
        disabled_messages: Iterable[type[events.Message]] | None = None,
        callbacks: Callbacks | None = None,
    ) -> None:
        """Initialize the MultiSelect control.

        Args:
            options: Options to select from. If no options are provided then
                `allow_blank` must be set to `True`.
            prompt: Text to show in the control when no option is selected.
            allow_blank: Enables or disables the ability to have the widget in a state
                with no selection made, in which case its value is set to the constant
                [`Select.BLANK`][textual.widgets.Select.BLANK].
            values: Initial value(s) selected. Should be one or mor of the values in `options`.
                If no initial value is set and `allow_blank` is `False`, the widget
                will auto-select the first available option.
            name: The name of the select control.
            id: The ID of the control in the DOM.
            classes: The CSS classes of the control.
            disabled: Whether the control is disabled or not.
            styles: Local inline styles to apply on top of the class' styles for only this instance.
            disabled_messages: List of messages to disable on this widget instance only.
            callbacks: Mapping of callbacks to send messages to instead of sending to default handler.

        Raises:
            EmptySelectError: If no options are provided and `allow_blank` is `False`.
        """
        super().__init__(
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
            styles=styles,
            disabled_messages=disabled_messages,
            callbacks=callbacks,
        )
        self._allow_blank = allow_blank
        self.prompt = prompt
        self._values = values
        self._options = []
        self._select_options = []
        self._setup_variables_for_options(options)

    def action_show_overlay(self) -> None:
        """Show the overlay."""
        select_current = self.query_one(SelectCurrent)
        select_current.has_value = bool(self.values) and self.values != BLANK
        self.expanded = True
        # If we haven't opened the overlay yet, highlight the first option.
        select_overlay = self.query_one(MultiSelectOverlay)
        if select_overlay.highlighted is None:
            select_overlay.action_first()

    def clear(self) -> None:
        """Clear the selection if `allow_blank` is `True`.

        Raises:
            InvalidSelectValueError: If `allow_blank` is set to `False`.
        """
        try:
            self.values = BLANK
        except InvalidSelectValueError:
            raise InvalidSelectValueError("Can't clear selection if allow_blank is set to False.") from None

    def compose(self) -> ComposeResult:
        """Compose MultiSelect with overlay and current value."""
        yield SelectCurrent(self.prompt)
        multiselect = MultiSelectOverlay()
        multiselect.allow_blank = self._allow_blank
        yield multiselect

    def _init_selected_options(self, hints: list[SelectType] | NoSelection = BLANK) -> None:
        """Initializes the selected option for the `MultiSelect`."""
        if hints == BLANK and not self._allow_blank:
            hints = [self._options[0][1]]
        self.values = hints

    def is_blank(self) -> bool:
        """Indicates whether this `MultiSelect` is blank or not.

        Returns:
            True if the selection is blank, False otherwise.
        """
        return self.values == BLANK

    def _on_mount(self, _: events.Mount) -> None:
        """Set initial values."""
        self._setup_options_renderables()
        self._init_selected_options(self._values)

    @on(SelectCurrent.Toggle)
    def _select_current_toggle(self, event: SelectCurrent.Toggle) -> None:
        """Show the overlay when toggled."""
        event.stop()
        self.expanded = not self.expanded

    @on(MultiSelectOverlay.Dismiss)
    def _select_overlay_dismiss(self, event: MultiSelectOverlay.Dismiss) -> None:
        """Dismiss the overlay."""
        event.stop()
        self.expanded = False
        if not event.lost_focus:
            # If the overlay didn't lose focus, don't to re-focus the select.
            self.focus()

    def set_options(
        self,
        options: Iterable[
            Selection[SelectionType] | tuple[TextType, SelectionType] | tuple[TextType, SelectionType, bool]
        ],
    ) -> None:
        """Set the options for the MultiSelect.

        This will reset the selection. The selection will be empty, if allowed, otherwise
        the first valid option is picked.

        Args:
            options: An iterable containing the renderable to display for each option (optional),
                the corresponding internal value (required), and the initial state of the selection (optional).

        Raises:
            EmptySelectError: If the options iterable is empty and `allow_blank` is `False`.
        """
        self._setup_variables_for_options(options)
        self._setup_options_renderables()
        self._init_selected_options()

    def _setup_options_renderables(self) -> None:
        """Sets up the `Selection` renderables associated with the `MultiSelect` options."""
        self._select_options: list[Selection] = [
            Selection(prompt, value, initial_state=initial_state) for prompt, value, initial_state in self._options
        ]
        selection_list = self.query_one(MultiSelectOverlay)
        selection_list.clear_options()
        for option in self._select_options:
            selection_list.add_option(option)

    def _setup_variables_for_options(
        self,
        options: Iterable[
            Selection[SelectionType] | tuple[TextType, SelectionType] | tuple[TextType, SelectionType, bool]
        ],
    ) -> None:
        """Setup function for the auxiliary variables related to options.

        This method sets up `self._options` and `self._legal_values`.
        """
        self._options: list[tuple[RenderableType, SelectType, bool]] = []
        for option in options:
            if not isinstance(option, tuple):
                option = (str(option), option, False)
            if not len(option) == 3:
                option = option + (False,)
            self._options.append(option)

        if not self._options and not self._allow_blank:
            raise EmptySelectError("MultiSelect options cannot be empty if selection can't be blank.")

        self._legal_values: set[SelectType | NoSelection] = {value for _, value, __ in self._options}
        if self._allow_blank:
            self._legal_values.add(BLANK)

    @on(MultiSelectOverlay.UpdateSelection)
    def _update_selection(self, event: MultiSelectOverlay.UpdateSelection) -> None:
        """Update the current selection."""
        event.stop()
        values = event.selected
        if values != self.values:
            self.values = values
            self.post_message(self.Changed(self, values))

    def _validate_values(
        self,
        values: list[SelectType] | NoSelection,
    ) -> list[SelectType] | NoSelection:
        """Ensure the new values only contain valid options.

        If `allow_blank` is `True`, `None` is also a valid value and corresponds to no selection.

        Raises:
            InvalidSelectValueError: If the new value does not correspond to any known value.
        """
        if not self._allow_blank and (not values or values == BLANK):
            raise InvalidSelectValueError("Can't clear selection if allow_blank is set to False.")
        new_values = []
        if values == BLANK:
            # Convert to a list for consistent check logic.
            new_values.append(BLANK)
        for sub_value in new_values:
            if sub_value not in self._legal_values:
                # It would make sense to use `None` to flag that the Select has no selection,
                # so we provide a helpful message to catch this mistake in case people didn't
                # realise we use a special value to flag "no selection".
                help_text = " Did you mean to use MultiSelect.clear()?" if sub_value is None else ""
                raise InvalidSelectValueError(f"Illegal multiselect value {sub_value!r}.{help_text}")
        return values

    def _watch_expanded(self, expanded: bool) -> None:
        """Display or hide overlay."""
        overlay = self.query_one(MultiSelectOverlay)
        self.set_class(expanded, "-expanded")
        if expanded:
            overlay.focus()
            if self.values == BLANK:
                overlay.deselect_all()
                self.query_one(SelectCurrent).has_value = False
            else:
                for _, value, __ in self._options:
                    if value in self.values:
                        overlay.select(value)
                self.query_one(SelectCurrent).has_value = True

    def _watch_prompt(self, prompt: str) -> None:
        """Update the current prompt when it changes."""
        if not self.is_mounted:
            return
        select_current = self.query_one(SelectCurrent)
        select_current.placeholder = prompt
        if not self._allow_blank:
            return
        if self.values == BLANK:
            select_current.update(BLANK)
        option_list = self.query_one(MultiSelectOverlay)
        option_list.replace_option_prompt_at_index(0, Text(prompt, style="dim"))

    def _watch_values(self, values: list[SelectType] | NoSelection) -> None:
        """Update the current value when it changes."""
        self._values = values if values else BLANK
        try:
            select_current = self.query_one(SelectCurrent)
        except NoMatches:
            pass
        else:
            if self.values == BLANK:
                select_current.update(BLANK)
            else:
                prompts = []
                for prompt, option_value, _ in self._options:
                    if option_value in values:
                        prompts.append(prompt)
                select_current.update(", ".join(prompts) or BLANK)
