"""Extended Textual radio button widget."""

from textual import widgets

from .._extensions import ToggleButtonInitExtension


class RadioButton(ToggleButtonInitExtension, widgets.RadioButton):  # pylint: disable=too-many-ancestors
    """An extended radio button widget that represents a boolean value."""
