"""Extended Textual Rule widget."""

from typing import Any
from typing import Iterable

from textual import events
from textual import widgets
from textual.widgets.rule import LineStyle
from textual.widgets.rule import RuleOrientation

from .._extensions import Callbacks
from .._extensions import WidgetExtension


class Rule(widgets.Rule, WidgetExtension):
    """An extended rule widget to separate content, similar to a `<hr>` HTML tag."""

    def __init__(
        self,
        orientation: RuleOrientation = "horizontal",
        line_style: LineStyle = "solid",
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        styles: dict[str, Any] | None = None,
        disabled_messages: Iterable[type[events.Message]] | None = None,
        callbacks: Callbacks | None = None,
    ) -> None:
        """Initialize the rule widget.

        Args:
            orientation: The orientation of the rule.
            line_style: The line style of the rule.
            name: The name of the widget.
            id: The ID of the widget in the DOM.
            classes: The CSS classes of the widget.
            disabled: Whether the widget is disabled or not.
            styles: Local inline styles to apply on top of the class' styles for only this instance.
            disabled_messages: List of messages to disable on this widget instance only.
            callbacks: Mapping of callbacks to send messages to instead of sending to default handler.
        """
        super().__init__(
            orientation=orientation,
            line_style=line_style,
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
