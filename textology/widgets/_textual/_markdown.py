"""Extended Textual Markdown widgets."""

from typing import Any
from typing import Callable

from textual import widgets
from textual.widgets._markdown import MarkdownIt

from .._extensions import WidgetExtension


class Markdown(WidgetExtension, widgets.Markdown):
    """An extended widget for rendering markdown."""

    def __init__(
        self,
        markdown: str | None = None,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        parser_factory: Callable[[], MarkdownIt] | None = None,
        **extension_configs: Any,
    ) -> None:
        """Initialize a Markdown widget.

        Args:
            markdown: String containing Markdown or None to leave blank for now.
            name: The name of the widget.
            id: The ID of the widget in the DOM.
            classes: The CSS classes of the widget.
            parser_factory: A factory function to return a configured MarkdownIt instance.
                If "None`, a "gfm-like" parser is used.
            extension_configs: Widget extension configurations, such as dynamically provided local callbacks by name.
        """
        super().__init__(
            markdown=markdown,
            name=name,
            id=id,
            classes=classes,
            parser_factory=parser_factory,
        )
        self.__extend_widget__(**extension_configs)


class MarkdownViewer(WidgetExtension, widgets.MarkdownViewer):
    """An extended Markdown viewer widget."""

    def __init__(
        self,
        markdown: str | None = None,
        *,
        show_table_of_contents: bool = True,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        parser_factory: Callable[[], MarkdownIt] | None = None,
        **extension_configs: Any,
    ) -> None:
        """Initialize a Markdown Viewer widget.

        Args:
            markdown: String containing Markdown, or None to leave blank.
            show_table_of_contents: Show a table of contents in a sidebar.
            name: The name of the widget.
            id: The ID of the widget in the DOM.
            classes: The CSS classes of the widget.
            parser_factory: A factory function to return a configured MarkdownIt instance.
                If "None", a "gfm-like" parser is used.
            extension_configs: Widget extension configurations, such as dynamically provided local callbacks by name.
        """
        super().__init__(
            markdown=markdown,
            show_table_of_contents=show_table_of_contents,
            name=name,
            id=id,
            classes=classes,
            parser_factory=parser_factory,
        )
        self.__extend_widget__(**extension_configs)
