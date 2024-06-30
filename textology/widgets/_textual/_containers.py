"""Extended Textual container widgets."""

from __future__ import annotations

from textual import containers

from .._extensions import WidgetFactory


class Center(WidgetFactory(containers.Center)):
    """An extended container which aligns children on the X axis."""


class Container(WidgetFactory(containers.Container)):
    """An extended, simple container widget, with vertical layout."""


class Grid(WidgetFactory(containers.Grid)):
    """An extended container with grid layout."""


class Horizontal(WidgetFactory(containers.Horizontal)):
    """An extended container with horizontal layout and no scrollbars."""


class HorizontalScroll(WidgetFactory(containers.HorizontalScroll)):
    """An extended container with horizontal layout and an automatic scrollbar on the Y axis."""


class Middle(WidgetFactory(containers.Middle)):
    """An extended container which aligns children on the Y axis."""


class PageContainer(Container):
    """Container used to display page contents, and signal to multi-page applications which ID to use in callbacks.

    If not used in a multi-page app, it is functionally the same as a Container.
    """


class ScrollableContainer(WidgetFactory(containers.ScrollableContainer)):
    """An extended scrollable container with vertical layout, and auto scrollbars on both axis."""


class Vertical(WidgetFactory(containers.Vertical)):
    """An extended container with vertical layout and no scrollbars."""


class VerticalScroll(WidgetFactory(containers.VerticalScroll)):
    """An extended container with vertical layout and an automatic scrollbar on the Y axis."""
