"""Tracking for values changes over time."""

from collections import deque
from typing import Any


class History:
    """Historical view of collection of values."""

    def __init__(
        self,
        history: list | None = None,
        max_length: int = 32,
    ) -> None:
        """Initialize the history object.

        Args:
            history: Initial values to store.
            max_length: Maximum amount of values to store before automatic removal.
        """
        self._history = deque(history or [], maxlen=max_length)
        self._index: int = max(len(self._history) - 1, 0)

    def add(
        self,
        value: str,
    ) -> None:
        """Add a new value to the history.

        Args:
            value: The new value to save.
        """
        # Remove all history after the current position, it is being rewritten.
        while len(self._history) - 1 > self._index:
            self._history.pop()
        self._history.append(value)
        self._index = len(self._history) - 1

    def back(self) -> int:
        """Go back in the history.

        Returns:
            The new index in the history.
        """
        if self._index:
            self._index -= 1
        return self._index

    def forward(self) -> int:
        """Go forward in the history.

        Returns:
            The new index in the history.
        """
        if self._index < len(self._history) - 1:
            self._index += 1
        return self._index

    @property
    def index(self) -> int | None:
        """Index of current value in history, or None if there is no current value."""
        return None if self.value is None else self._index

    def pop(self) -> Any:
        """Remove and return the rightmost value.

        Returns:
            The original value at the location.
        """
        self._history.pop()
        return self.remove(len(self._history) - 1)

    def remove(
        self,
        index: int,
    ) -> Any:
        """Remove a value from the history.

        Args:
            index: Position in the history to remove.

        Returns:
            The original value at the location.
        """
        value = None
        if 0 <= index <= len(self._history) - 1:
            value = self._history[index]
            del self._history[index]
            if self._index == index:
                self._index = index - 1
        return value

    @property
    def value(self) -> Any:
        """Current value in the history, or None if there is no current value."""
        try:
            return self._history[self._index]
        except IndexError:
            return None

    @property
    def values(self) -> list:
        """All values in the history."""
        return list(self._history)
