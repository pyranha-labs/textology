"""Custom textual Widgets extensions."""

import time
from inspect import isawaitable
from typing import Any
from typing import Awaitable
from typing import Callable
from typing import Coroutine
from typing import Generator
from typing import Iterable

from rich.console import RenderableType
from rich.text import TextType
from textual import events
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget as TextualWidget
from textual.widgets import Static as TextualStatic
from textual.widgets._toggle_button import ToggleButton as TextualToggleButton

Callback = Callable | Coroutine


class Clickable(TextualWidget):
    """Add reactive attributes for clicking on a widget.

    Use "update_n_clicks()" to trigger reactive attributes in a consistent manner.
    """

    # Number of times the widget has been clicked on.
    n_clicks: int = reactive(0, repaint=False, init=False)
    # Time (in milliseconds since 1970) since the last time n_clicks updated.
    n_clicks_timestamp: float = reactive(-1.0, repaint=False, init=False)
    # Disable n_clicks* properties.
    disable_n_clicks: bool = reactive(False, repaint=False, init=False)

    def update_n_clicks(self) -> None:
        """Update the number of times the widget has been clicked by one."""
        if not self.disable_n_clicks:
            self.n_clicks += 1

    def watch_n_clicks(self, _: int) -> None:
        """Monitor click count to update the last time clicked."""
        self.n_clicks_timestamp = time.time()


class WidgetExtension(TextualWidget):
    """Extension for textual widgets to allow various overrides and control of behaviors at an instance level.

    Use `WidgetExtension` class, if:
        - Subclassing a Textual widget, and overriding the `__init__`.
        - Example: `class MyButton(Button, WidgetExtension):` + `def __init__(self, ...)`
    Use `Widget` class, if:
        - Creating a new widget, that inherits directly from `Widget`.
        - Example: `class MyWidget(Widget):`
    Use `WidgetFactory` function if:
        - Subclassing a Textual widget, that uses the `__init__` from Textual `Widget`, but needs extensions.
        - Example: `class MyContainer(WidgetFactory(Container))

    Key Features:
    - Handles messages at lowest level available for control of disables, intercepts, and more per instance.
    - Allows declaring "on_*" functions for callbacks per instance during instantiation.
    - Allows declaring "style" attributes per instance during instantiation.

    Compared to disabling and intercepting messages at "post_message" level, this extension ensures that any
    messages added directly to the queue are handled based on Widget rules. Widgets that inherit from this
    class can also "intercept" the messages to route them manually, swap them with new messages, absorb them, etc.

    If a message is not disabled, or returned after being intercepted, it will then route to a local callback
    if one was provided to the widget on instantiation. Local callbacks provide additional isolation of message
    handling logic from the global app namespace. If there is no local callback for a message, or the local callback
    returns True (for continue), the message will be sent to the original widget message handler, and propagate
    throughout the app as normal.
    """

    default_disabled_messages: Iterable[type[events.Message]] = ()

    def __extend_widget__(
        self,
        styles: dict[str, Any] | None = None,
        disabled_messages: Iterable[type[events.Message]] | None = None,
        callbacks: dict[str, Callback] | None = None,
    ) -> None:
        """Set up the widget's extensions.

        Args:
            styles: Local inline styles to apply on top of the class' styles for only this instance.
            disabled_messages: List of messages to disable on this widget instance only.
                Defaults to class default_disabled_messages attribute if None.
            callbacks: Mapping of callbacks to send messages to instead of sending to default handler.
                Callbacks behave the same as "on_*" functions declared at class level.
                Return "True" in callbacks to send the messages to the default widget handler.
                May be provided as direct arguments to "additional_configs". e.g. "on_button_pressed=on_press"
        """
        self._local_callback_map = {}

        if styles:
            self.__extend_widget_styles__(styles)

        if callbacks:
            self.__extend_widget_messaging_callbacks__(callbacks)

        # Allow messages to be disabled for this instance of the widget only, or use subclass defaults.
        if disabled_messages is None:
            disabled_messages = self.default_disabled_messages
        if disabled_messages:
            self.disable_messages(*disabled_messages)

    def __extend_widget_messaging_callbacks__(
        self,
        local_callbacks: dict[str, Callback],
    ) -> None:
        """Validate and set up message callbacks."""
        for key, value in local_callbacks.items():
            if not key.startswith("on_"):
                raise ValueError(
                    'Callbacks must start with "on_" and end with the name of the event type in camel_case'
                )
            self._local_callback_map[key] = value

    def __extend_widget_styles__(self, styles: dict) -> None:
        """Apply inline/local styles for the instance."""
        for key, value in styles.items():
            setattr(self.styles, key, value)

    def action_focus_next(self) -> None:
        """Focus the next widget when the action is called."""
        self.app.action_focus_next()

    def action_focus_previous(self) -> None:
        """Focus the previous widget when the action is called."""
        self.app.action_focus_previous()

    def after(
        self,
        awaitable: Awaitable,
        func: Callable,
        *args: Any,
        **kwargs: Any,
    ) -> bool:
        """Await a coroutine's results and then run a function.

        Args:
            awaitable: Async result returned from a coroutine.
            func: The function to run after the awaitable has completed.
            args: Positional arguments to pass to the function run after awaitable completes.
            kwargs: Keyword arguments to pass to the function run after awaitable completes.

        Returns:
            True if the message was posted, False if this widget was closed / closing.
        """

        async def awaiter() -> None:
            """Coroutine to await an awaitable returned from another function, before running final function."""
            await awaitable
            result = func(*args, **kwargs)
            if isawaitable(result):
                await result

        return self.post_message(events.Callback(callback=awaiter))

    def disable_child_messages(
        self,
        *messages: type[events.Message],
    ) -> None:
        """Recursively disable message types from being processed on all child widgets.

        Args:
            messages: Message types to disable on all children of this widget.
        """
        for child in self.walk_all_children():
            child.disable_messages(*messages)

    async def _handle_local_callback(self, message: Message) -> bool:
        """Route message to a local callback if available, or recommend sending to native widget message handler.

        If callback manually returns a truthy value, the message will also be handled by native widget message handler.
        """
        handle_natively = True
        handler_name = message.handler_name
        if handler_name in self._local_callback_map:
            handle_natively = self._local_callback_map[handler_name](message)
            if isawaitable(handle_natively):
                handle_natively = await handle_natively
        return handle_natively

    async def intercept_message(self, message: Message) -> Message | None:
        """Intercept a message for this widget before processing.

        Args:
            message: Original message pending processing.

        Returns:
            Message to process after being intercepted by this widget, None to disable further processing.
        """
        # Defaults to returning to the original message to process as normal.
        return message

    async def _on_message(self, message: Message) -> None:
        """Override default message processing to allow disables, intercepts, and local callbacks, at lowest level."""
        if not self.check_message_enabled(message):
            # Ensure no other handlers see the message as being valid for further processing.
            message.stop()
            message.prevent_default()
            return

        message = await self.intercept_message(message)
        if not message:
            return
        if not await self._handle_local_callback(message):
            message.stop()
            message.prevent_default()
        else:
            await super()._on_message(message)
        return None

    def _post_mount(self) -> None:
        """Overrides native post mount actions to register observer support."""
        super()._post_mount()
        attach_to_observers = getattr(self.app, "attach_to_observers", None)
        if attach_to_observers:
            attach_to_observers(self)
        if self.id:
            _register_reactive_observers = getattr(self.app, "_register_reactive_observers", None)
            if _register_reactive_observers:
                _register_reactive_observers(self)

    def walk_all_children(self) -> Generator[TextualWidget, None, None]:
        """Walk the subtree rooted at this node, and return every descendant encountered.

        Compared to walk_children, this function will also walk all pending children. Pending children
        will be walked first, followed by results from walk_children().

        Yields:
            Every child, pending or standard, starting from the top down, and pending before standard.
        """
        for child in walk_all_children(self):
            yield child


class Static(TextualStatic, WidgetExtension):
    """An extended widget to display simple static content, or use as a base class for more complex widgets.

    Includes all extensions provided by WidgetExtension, and automatically calls the extension set up.
    See WidgetExtension for full details on all extended features and proper usage.
    """

    def __init__(  # pylint: disable=too-many-arguments
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
        styles: dict[str, Any] | None = None,
        disabled_messages: Iterable[type[events.Message]] | None = None,
        callbacks: dict[str, Callback] | None = None,
    ) -> None:
        """Initialize a Static widget with extension arguments.

        Args:
            renderable: A Rich renderable, or string containing console markup.
            expand: Expand content if required to fill container.
            shrink: Shrink content if required to fill container.
            markup: True if markup should be parsed and rendered.
            name: Name of widget.
            id: ID of Widget.
            classes: Space separated list of class names.
            disabled: Whether the static is disabled or not.
            styles: Local inline styles to apply on top of the class' styles for only this instance.
            disabled_messages: List of messages to disable on this widget instance only.
            callbacks: Mapping of callbacks to send messages to instead of sending to default handler.
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
        self.__extend_widget__(
            styles=styles,
            disabled_messages=disabled_messages,
            callbacks=callbacks,
        )


class ToggleButton(TextualToggleButton, WidgetExtension):
    """An extended base toggle button widget.

    Includes all extensions provided by WidgetExtension, and automatically calls the extension set up.
    See WidgetExtension for full details on all extended features and proper usage.
    """

    def __init__(  # pylint: disable=too-many-arguments
        self,
        label: TextType = "",
        value: bool = False,
        button_first: bool = True,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        styles: dict[str, Any] | None = None,
        disabled_messages: Iterable[type[events.Message]] | None = None,
        callbacks: dict[str, Callback] | None = None,
    ) -> None:
        """Initialize the toggle.

        Args:
            label: The label for the toggle.
            value: The initial value of the toggle.
            button_first: Should the button come before the label, or after?
            name: The name of the toggle.
            id: The ID of the toggle in the DOM.
            classes: The CSS classes of the toggle.
            disabled: Whether the button is disabled or not.
            styles: Local inline styles to apply on top of the class' styles for only this instance.
            disabled_messages: List of messages to disable on this widget instance only.
            callbacks: Mapping of callbacks to send messages to instead of sending to default handler.
        """
        super().__init__(
            label=label,
            value=value,
            button_first=button_first,
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


class Widget(WidgetExtension):
    """Extended widget to allow various overrides and control of behaviors at an instance level.

    Includes all extensions provided by WidgetExtension, and automatically calls the extension set up.
    See WidgetExtension for full details on all extended features and proper usage.
    """

    def __init__(
        self,
        *children: TextualWidget,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        styles: dict[str, Any] | None = None,
        disabled_messages: Iterable[type[events.Message]] | None = None,
        callbacks: dict[str, Callback] | None = None,
    ) -> None:
        """Initialize a Widget with support for extension arguments.

        Args:
            *children: Child widgets.
            name: The name of the widget.
            id: The ID of the widget in the DOM.
            classes: The CSS classes for the widget.
            disabled: Whether the widget is disabled or not.
            styles: Local inline styles to apply on top of the class' styles for only this instance.
            disabled_messages: List of messages to disable on this widget instance only.
            callbacks: Mapping of callbacks to send messages to instead of sending to default handler.
        """
        super().__init__(
            *children,
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


def StaticFactory(cls: type[Static]) -> type[Static]:  # pylint: disable=invalid-name
    """Create a Static subclass tha preserves the original class as the primary, and uses the extended init.

    See `WidgetExtension` for details on proper usage, and when to use this over alternatives.

    Args:
        cls: Original class that is a subclass of `Static`.

    Return:
        New class with the original as the base, combined with widget extensions, and init override.
    """

    class ExtendedStatic(cls, Static):
        """An extended widget to display simple static content, or use as a base class for more complex widgets."""

        # Redeclare init from class otherwise E1120 errors are thrown by all subclasses.
        def __init__(  # pylint: disable=too-many-arguments
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
            styles: dict[str, Any] | None = None,
            disabled_messages: Iterable[type[events.Message]] | None = None,
            callbacks: dict[str, Callback] | None = None,
        ) -> None:
            """Initialize a Static widget with extension arguments.

            Args:
                renderable: A Rich renderable, or string containing console markup.
                expand: Expand content if required to fill container.
                shrink: Shrink content if required to fill container.
                markup: True if markup should be parsed and rendered.
                name: Name of widget.
                id: ID of Widget.
                classes: Space separated list of class names.
                disabled: Whether the static is disabled or not.
                styles: Local inline styles to apply on top of the class' styles for only this instance.
                disabled_messages: List of messages to disable on this widget instance only.
                callbacks: Mapping of callbacks to send messages to instead of sending to default handler.
            """
            Static.__init__(
                self,
                renderable,
                expand=expand,
                shrink=shrink,
                markup=markup,
                name=name,
                id=id,
                classes=classes,
                disabled=disabled,
                styles=styles,
                disabled_messages=disabled_messages,
                callbacks=callbacks,
            )

    return ExtendedStatic


def ToggleButtonFactory(cls: type[TextualToggleButton]) -> type[ToggleButton]:  # pylint: disable=invalid-name
    """Create a ToggleButton subclass tha preserves the original class as the primary, and uses the extended init.

    See `WidgetExtension` for details on proper usage, and when to use this over alternatives.

    Args:
        cls: Original class that is a subclass of `ToggleButton`.

    Return:
        New class with the original as the base, combined with widget extensions, and init override.
    """

    class ExtendedToggleButton(cls, ToggleButton):
        """An extended base toggle button widget."""

        # Redeclare init from class otherwise E1120 errors are thrown by all subclasses.
        def __init__(  # pylint: disable=too-many-arguments
            self,
            label: TextType = "",
            value: bool = False,
            button_first: bool = True,
            *,
            name: str | None = None,
            id: str | None = None,
            classes: str | None = None,
            disabled: bool = False,
            styles: dict[str, Any] | None = None,
            disabled_messages: Iterable[type[events.Message]] | None = None,
            callbacks: dict[str, Callback] | None = None,
        ) -> None:
            """Initialize the toggle.

            Args:
                label: The label for the toggle.
                value: The initial value of the toggle.
                button_first: Should the button come before the label, or after?
                name: The name of the toggle.
                id: The ID of the toggle in the DOM.
                classes: The CSS classes of the toggle.
                disabled: Whether the button is disabled or not.
                styles: Local inline styles to apply on top of the class' styles for only this instance.
                disabled_messages: List of messages to disable on this widget instance only.
                callbacks: Mapping of callbacks to send messages to instead of sending to default handler.
            """
            ToggleButton.__init__(
                self,
                label=label,
                value=value,
                button_first=button_first,
                name=name,
                id=id,
                classes=classes,
                disabled=disabled,
                styles=styles,
                disabled_messages=disabled_messages,
                callbacks=callbacks,
            )

    return ExtendedToggleButton


def WidgetFactory(cls: type[TextualWidget]) -> type[Widget]:  # pylint: disable=invalid-name
    """Create a Widget subclass tha preserves the original class as the primary, and uses the extended init.

    See `WidgetExtension` for details on proper usage, and when to use this over alternatives.

    Args:
        cls: Original class that is a subclass of `Widget`.

    Return:
        New class with the original as the base, combined with widget extensions, and init override.
    """

    class ExtendedWidget(cls, Widget):
        """Extended widget to allow various overrides and control of behaviors at an instance level."""

        # Redeclare init from class otherwise E1120 errors are thrown by all subclasses.
        def __init__(
            self,
            *children: TextualWidget,
            name: str | None = None,
            id: str | None = None,
            classes: str | None = None,
            disabled: bool = False,
            styles: dict[str, Any] | None = None,
            disabled_messages: Iterable[type[events.Message]] | None = None,
            callbacks: dict[str, Callback] | None = None,
        ) -> None:
            """Initialize a Widget with support for extension arguments.

            Args:
                *children: Child widgets.
                name: The name of the widget.
                id: The ID of the widget in the DOM.
                classes: The CSS classes for the widget.
                disabled: Whether the widget is disabled or not.
                styles: Local inline styles to apply on top of the class' styles for only this instance.
                disabled_messages: List of messages to disable on this widget instance only.
                callbacks: Mapping of callbacks to send messages to instead of sending to default handler.
            """
            Widget.__init__(
                self,
                *children,
                name=name,
                id=id,
                classes=classes,
                disabled=disabled,
                styles=styles,
                disabled_messages=disabled_messages,
                callbacks=callbacks,
            )

    return ExtendedWidget


def walk_all_children(widget: TextualWidget) -> Generator[TextualWidget, None, None]:
    """Walk the subtree of a node, and return every descendant encountered.

    Compared to walk_children, this function will also walk all pending children. Pending children
    will be walked first, followed by results from walk_children().

    Yields:
        Every child, pending or standard, starting from the top down, and pending before standard.
    """
    for pending_child in getattr(widget, "_pending_children", []):
        yield pending_child
        for nested_child in walk_all_children(pending_child):
            yield nested_child
    for child in widget.walk_children():
        yield child
