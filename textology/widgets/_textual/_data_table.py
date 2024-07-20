"""Extended Textual DataTable widget."""

from typing import Any
from typing import Iterable

from textual import events
from textual import widgets
from typing_extensions import Literal

from .._extensions import Callbacks
from .._extensions import WidgetExtension


class DataTable(widgets.DataTable, WidgetExtension):  # pylint: disable=too-many-ancestors
    """An extended tabular widget that contains data."""

    def __init__(  # pylint: disable=too-many-locals,too-many-arguments
        self,
        *,
        show_header: bool = True,
        show_row_labels: bool = True,
        fixed_rows: int = 0,
        fixed_columns: int = 0,
        zebra_stripes: bool = False,
        header_height: int = 1,
        show_cursor: bool = True,
        cursor_foreground_priority: Literal["renderable", "css"] = "css",
        cursor_background_priority: Literal["renderable", "css"] = "renderable",
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        styles: dict[str, Any] | None = None,
        disabled_messages: Iterable[type[events.Message]] | None = None,
        callbacks: Callbacks | None = None,
    ) -> None:
        """Initialize the data table widget.

        Args:
            show_header: Whether to show the table header.
            show_row_labels: Whether to show labels on every row.
            fixed_rows: Fixed number of rows to display.
            fixed_columns: Fixed number of columns to display
            zebra_stripes: Whether to display the rows with alternating background highlight style.
            show_cursor: Whether to highlight the currently active cursor highlight.
            header_height: Height the header row.
            cursor_foreground_priority: Whether to prioritize the cursor CSS foreground or the renderable foreground.
            cursor_background_priority: Whether to prioritize the cursor CSS background or the renderable background.
            name: The name of the content switcher.
            id: The ID of the content switcher in the DOM.
            classes: The CSS classes of the content switcher.
            disabled: Whether the content switcher is disabled or not.
            styles: Local inline styles to apply on top of the class' styles for only this instance.
            disabled_messages: List of messages to disable on this widget instance only.
            callbacks: Mapping of callbacks to send messages to instead of sending to default handler.
        """
        super().__init__(
            show_header=show_header,
            show_row_labels=show_row_labels,
            fixed_rows=fixed_rows,
            fixed_columns=fixed_columns,
            zebra_stripes=zebra_stripes,
            header_height=header_height,
            show_cursor=show_cursor,
            cursor_foreground_priority=cursor_foreground_priority,
            cursor_background_priority=cursor_background_priority,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self.__extend_widget__(
            styles=styles,
            disabled_messages=disabled_messages,
            callbacks=callbacks,
        )
