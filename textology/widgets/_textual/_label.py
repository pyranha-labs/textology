"""Extended Textual label widget for displaying text-oriented renderables."""

from textual import widgets

from .._extensions import StaticFactory


class Label(StaticFactory(widgets.Label)):
    """An extended, simple, label widget for displaying text-oriented renderables."""
