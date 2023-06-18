"""Logging utilities."""

import logging
from typing import Any


class NullLogger(logging.Logger):
    """Dummy logger to allow null routing all logging messages."""

    def __getattribute__(self, name: str) -> Any:
        """Null route all attribute requests."""
        if name != "_null_route":
            return self._null_route
        return super().__getattribute__(name)

    def _null_route(self, *args: Any, **kwargs: Any) -> None:
        """Null route any callable action."""
