"""Extended Textual Loading Indicator widget."""

from textual import widgets

from .._extensions import WidgetInitExtension


class LoadingIndicator(WidgetInitExtension, widgets.LoadingIndicator):
    """An extended display for an animated loading indicator."""
