"""Extended Textual Tab widgets."""

from typing import Any
from typing import Iterable

from rich.text import TextType
from textual import events
from textual import widgets

from .._extensions import Callbacks
from .._extensions import WidgetExtension


class Tab(widgets.Tab, WidgetExtension):
    """An extended widget to manage a single tab within a Tabs widget."""

    def __init__(
        self,
        label: TextType,
        *,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        styles: dict[str, Any] | None = None,
        disabled_messages: Iterable[type[events.Message]] | None = None,
        callbacks: Callbacks | None = None,
    ) -> None:
        """Initialize a Tab.

        Args:
            label: The label to use in the tab.
            id: Optional ID for the widget.
            classes: Space separated list of class names.
            disabled: Whether the tab is disabled or not.
            styles: Local inline styles to apply on top of the class' styles for only this instance.
            disabled_messages: List of messages to disable on this widget instance only.
            callbacks: Mapping of callbacks to send messages to instead of sending to default handler.
        """
        super().__init__(
            label,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self.__extend_widget__(
            styles=styles,
            disabled_messages=disabled_messages,
            callbacks=callbacks,
        )


class Tabs(widgets.Tabs, WidgetExtension):
    """An extended row of tabs."""

    def __init__(
        self,
        *tabs: Tab | TextType,
        active: str | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        styles: dict[str, Any] | None = None,
        disabled_messages: Iterable[type[events.Message]] | None = None,
        callbacks: Callbacks | None = None,
    ) -> None:
        """Initialize a Tabs widget.

        Args:
            *tabs: Positional argument should be explicit Tab objects, or a str or Text.
            active: ID of the tab which should be active on start.
            name: Optional name for the input widget.
            id: Optional ID for the widget.
            classes: Optional initial classes for the widget.
            disabled: Whether the input is disabled or not.
            styles: Local inline styles to apply on top of the class' styles for only this instance.
            disabled_messages: List of messages to disable on this widget instance only.
            callbacks: Mapping of callbacks to send messages to instead of sending to default handler.
        """
        super().__init__(
            *tabs,
            active=active,
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
