"""Widget to display simple text content, or hide when no message."""

from textual.reactive import reactive

from ._extensions import Static


class PopupText(Static):
    """A widget for displaying text content when available, or hiding when unavailable."""

    value = reactive(None)

    def watch_value(self, new_value: str | None) -> None:
        """Update the displayed text when a new value is set.

        Args:
            new_value: New text value.
        """
        new_value = str(new_value) if new_value is not None else ""
        self.styles.display = "block" if new_value else "none"
        self.update(new_value)
