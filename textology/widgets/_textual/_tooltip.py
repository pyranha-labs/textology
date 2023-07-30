"""Extended Textual tooltip widget."""

from textual import widgets

from .._extensions import StaticInitExtension


class Tooltip(StaticInitExtension, widgets.Tooltip):
    """An extended widget for displaying short tip messages."""
