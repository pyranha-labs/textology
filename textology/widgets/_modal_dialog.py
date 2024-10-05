"""Modal screen to show a provided widget and add basic navigation."""

from asyncio import Future
from typing import ClassVar

from textual.app import App
from textual.app import ComposeResult
from textual.binding import Binding
from textual.binding import BindingType
from textual.screen import ModalScreen
from textual.screen import ScreenResultCallbackType
from textual.screen import ScreenResultType
from textual.widget import AwaitMount
from textual.widget import Widget


class ModalDialog(ModalScreen):
    """Basic modal screen to show a provided widget and add basic navigation."""

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("escape", "dismiss(None)", show=False),
    ]
    DEFAULT_CSS = """
    ModalDialog {
        align: center middle;
        background: $surface 50%;
    }
    """

    def __init__(
        self,
        child: Widget,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """Initialize dialog content.

        Args:
            child: Widget to display when dialog is mounted.
            id: The ID of the dialog in the DOM.
            classes: The CSS classes for the dialog.
        """
        super().__init__(id=id, classes=classes)
        self.child = child

    def compose(self) -> ComposeResult:
        """Show the child provided on instantiation."""
        yield self.child

    def show(
        self,
        app: App,
        callback: ScreenResultCallbackType[ScreenResultType] | None = None,
        wait_for_dismiss: bool = False,
    ) -> AwaitMount | Future[ScreenResultType]:
        """Display the dialog on top of an application.

        Alias for app.push_screen().

        Args:
            app: Application to push the dialog on top of.
            callback: An optional callback function that will be called if the screen is dismissed with a result.
            wait_for_dismiss: Whether the return will wait for the screen to dismiss, or mount.
                Should only be set to True when running in a worker. See `App.push_screen` for more details.

        Returns:
            An optional awaitable that awaits the mounting of the screen and its children, or the result of the screen.
        """
        return app.push_screen(self, callback=callback, wait_for_dismiss=wait_for_dismiss)
