"""Extended Textual checkbox widget."""

from textual import widgets

from .._extensions import ToggleButtonFactory


class Checkbox(ToggleButtonFactory(widgets.Checkbox)):  # pylint: disable=too-many-ancestors
    """An extended checkbox widget that represents a boolean value."""
