"""Extended Textual container widgets."""

from __future__ import annotations

from textual import containers

from .._extensions import WidgetInitExtension


class Center(WidgetInitExtension, containers.Center):
    """An extended container which aligns children on the X axis."""


class Container(WidgetInitExtension, containers.Container):
    """An extended, simple container widget, with vertical layout."""


class Grid(WidgetInitExtension, containers.Grid):
    """An extended container with grid layout."""


class Horizontal(WidgetInitExtension, containers.Horizontal):
    """An extended container with horizontal layout and no scrollbars."""


class HorizontalScroll(WidgetInitExtension, containers.HorizontalScroll):
    """An extended container with horizontal layout and an automatic scrollbar on the Y axis."""


class Middle(WidgetInitExtension, containers.Middle):
    """An extended container which aligns children on the Y axis."""


class PageContainer(Container):
    """Container used to display page contents, and signal to multi-page applications which ID to use in callbacks.

    If not used in a multi-page app, it is functionally the same as a Container.
    """


class ScrollableContainer(containers.ScrollableContainer):
    """An extended scrollable container with vertical layout, and auto scrollbars on both axis."""


class Vertical(WidgetInitExtension, containers.Vertical):
    """An extended container with vertical layout and no scrollbars."""


class VerticalScroll(WidgetInitExtension, containers.VerticalScroll):
    """An extended container with vertical layout and an automatic scrollbar on the Y axis."""
