"""Extended Textual checkbox widget."""

from textual import widgets

from .._extensions import ToggleButtonInitExtension


class Checkbox(ToggleButtonInitExtension, widgets.Checkbox):  # pylint: disable=too-many-ancestors
    """An extended checkbox widget that represents a boolean value."""
