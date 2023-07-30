"""Extended Textual DataTable widget."""

from typing import Any

from textual import widgets
from typing_extensions import Literal

from .._extensions import WidgetExtension


class DataTable(WidgetExtension, widgets.DataTable):  # pylint: disable=too-many-ancestors
    """An extended tabular widget that contains data."""

    def __init__(
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
        **extension_configs: Any,
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
            extension_configs: Widget extension configurations, such as dynamically provided local callbacks by name.
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
        self.__extend_widget__(**extension_configs)
