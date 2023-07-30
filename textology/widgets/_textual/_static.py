"""Extended Textual widget to display simple static content, or use as a base class for more complex widgets."""

from textual import widgets

from .._extensions import StaticInitExtension


class Static(StaticInitExtension, widgets.Static):
    """An extended widget to display simple static content, or use as a base class for more complex widgets."""
