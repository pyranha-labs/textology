"""Basic application for unit tests."""

from textual.app import ComposeResult

from textology import apps
from textology import widgets


class BasicApp(apps.ExtendedApp):
    """Simple application with basic elements for testing interactions and snapshots."""

    def compose(self) -> ComposeResult:
        """Provide basic layout with one interactive, and one non-interactive, element."""
        yield widgets.Button("Click me!", id="btn")
        yield widgets.Store("Update me!", id="store")


app = BasicApp()
