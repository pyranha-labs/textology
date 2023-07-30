"""Custom textual Widgets extensions."""

import time
from inspect import isawaitable
from typing import Any
from typing import Awaitable
from typing import Callable

from rich.console import RenderableType
from rich.text import TextType
from textual import events
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget


class Clickable:
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


class WidgetExtension:
    """Extension for textual widgets to allow various overrides and control of behaviors at an instance level.

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

    If creating a new basic widget, use WidgetInitExtension + Widget instead. If subclassing an existing,
    basic, textual widget,  the extension class must be placed before base class to ensure custom behaviors
    take priority. Example:
        class MyContainer(WidgetExtension, Container):
            ...
    """

    default_disabled_messages = []

    def __extend_widget__(
        self,
        disable_messages: list[events.Message] | None = None,
        local_callbacks: dict[str, Callable] | None = None,
        styles: dict[str, Any] | None = None,
        **additional_configs: Any,
    ) -> None:
        """Set up the widget's extensions.

        Args:
            disable_messages: List of messages to disable on this widget instance only.
                Defaults to class default_disabled_messages attribute if None.
            local_callbacks: Mapping of callbacks to send messages to instead of sending to default handler.
                Callbacks behave the same as "on_*" functions declared at class level.
                Return "True" in callbacks to send the messages to the default widget handler.
                May be provided as direct arguments to "additional_configs". e.g. "on_button_pressed=on_press"
            additional_configs: Additional configurations, such as dynamically provided local callbacks by name.
            styles: Local inline styles to apply on top of the classes styles for only this instance.
        """
        self._local_callback_map = {}

        if styles:
            self.__extend_widget_styles__(styles)

        # Allow callback to be provided as an explicit dictionary, or as dynamic kwargs.
        if not local_callbacks:
            found_callbacks = {}
            for key, value in additional_configs.items():
                if key.startswith("on_") and callable(value):
                    found_callbacks[key] = value
            local_callbacks = found_callbacks
        if local_callbacks:
            self.__extend_widget_messaging_callbacks__(local_callbacks)

        # Allow messages to be disabled for this instance of the widget only, or use subclass defaults.
        if disable_messages is None:
            disable_messages = self.default_disabled_messages
        if disable_messages:
            self.disable_messages(*disable_messages)

    def __extend_widget_messaging_callbacks__(
        self,
        local_callbacks: dict[str, Callable],
    ) -> None:
        """Validate and set up message callbacks."""
        for key, value in local_callbacks.items():
            if not key.startswith("on_"):
                continue
            self._local_callback_map[key] = value

    def __extend_widget_styles__(self, styles: dict) -> None:
        """Apply inline/local styles for the instance."""
        for key, value in styles.items():
            setattr(self.styles, key, value)

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


class StaticInitExtension(WidgetExtension):
    """Extension for textual widgets that inherit from Static class.

    Includes all extensions provided by WidgetExtension, and automatically calls the extension set up.
    See WidgetExtension for full details on all extended features.

    Example:
        class Label(StaticInitExtension, widgets.Label):
            ...
    """

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


class ToggleButtonInitExtension(WidgetExtension):
    """Extension for textual widgets that inherit from ToggleButton class.

    Includes all extensions provided by WidgetExtension, and automatically calls the extension set up.
    See WidgetExtension for full details on all extended features.

    Example:
        class Checkbox(ToggleButtonInitExtension, containers.Checkbox):
            ...
    """

    def __init__(
        self,
        label: TextType = "",
        value: bool = False,
        button_first: bool = True,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        **extension_configs: Any,
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
            extension_configs: Widget extension configurations, such as dynamically provided local callbacks by name.
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
        self.__extend_widget__(**extension_configs)


class WidgetInitExtension(WidgetExtension):
    """Extension for textual widgets that inherit from base Widget class.

    Includes all extensions provided by WidgetExtension, and automatically calls the extension set up.
    See WidgetExtension for full details on all extended features.

    Example:
        class Container(WidgetInitExtension, containers.Container):
            ...
    """

    def __init__(
        self,
        *children: Widget,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        **extension_configs: Any,
    ) -> None:
        """Initialize a Widget with support for extension arguments.

        Args:
            *children: Child widgets.
            name: The name of the widget.
            id: The ID of the widget in the DOM.
            classes: The CSS classes for the widget.
            disabled: Whether the widget is disabled or not.
            extension_configs: Widget extension configurations, such as dynamically provided local callbacks by name.
        """
        super().__init__(
            *children,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self.__extend_widget__(**extension_configs)
