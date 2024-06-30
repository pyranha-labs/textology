"""Extended Textual tooltip widget."""

from textual import widgets

from .._extensions import StaticFactory


class Tooltip(StaticFactory(widgets.Tooltip)):
    """An extended widget for displaying short tip messages."""
