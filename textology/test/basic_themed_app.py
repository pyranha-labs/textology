"""Basic themed application for unit tests."""

from textual.app import ComposeResult

from textology import apps
from textology import widgets


class BasicThemedApp(apps.ExtendedApp):
    """Simple themed application with basic elements for testing interactions and snapshots."""

    CSS_THEMES = {
        "green": [
            "basic_themed_app-green_btn.css",
        ],
        "white": [
            "basic_themed_app-white_border.css",
        ],
    }

    def compose(self) -> ComposeResult:
        """Provide basic layout."""
        yield widgets.Button("Click me!", id="btn")


app = BasicThemedApp()
