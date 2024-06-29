"""Extended Rich text objects with additional customization."""

from __future__ import annotations

from typing import Literal
from typing import Optional

from rich.console import JustifyMethod
from rich.console import OverflowMethod
from rich.style import Style
from rich.text import DEFAULT_OVERFLOW
from rich.text import Span
from rich.text import Text as RichText
from rich.text import cell_len
from rich.text import set_cell_size
from typing_extensions import override

OverflowSide = Literal["left", "right"]


class Text(RichText):
    """Extended Rich text with standard color/style controls, and additional overflow controls."""

    __slots__ = [
        "_overflow_side",
        "_overflow_char",
    ]

    def __init__(
        self,
        text: str = "",
        style: str | Style = "",
        *,
        justify: JustifyMethod | None = None,
        overflow: OverflowMethod | None = None,
        overflow_side: OverflowSide = "right",
        overflow_char: OverflowSide = "…",
        no_wrap: bool | None = None,
        end: str = "\n",
        tab_size: Optional[int] = None,
        spans: list[Span] | None = None,
    ) -> None:
        """Initialize the text with style and overflow controls.

        Args:
            text: Default unstyled text.
            style: Base style for text.
            justify: Justify method as "left", "center", "full", "right".
            overflow: Overflow method: "crop", "fold", "ellipsis".
            overflow_side: Which side of the text to show ellipsis on as "left" or "right".
            overflow_char: Which character to use for the ellipsis.
            no_wrap: Disable text wrapping, or None for default.
            end: Character to end text with.
            tab_size: Number of spaces per tab, or ``None`` to use ``console.tab_size``.
            spans: A list of predefined style spans. Defaults to None.
        """
        super().__init__(
            text,
            style,
            justify=justify,
            overflow=overflow,
            no_wrap=no_wrap,
            end=end,
            tab_size=tab_size,
            spans=spans,
        )
        if len(overflow_char) > 1:
            raise ValueError("Overflow characters must be a single character")
        self._overflow_side = overflow_side
        self._overflow_char = overflow_char

    @override
    def blank_copy(self, plain: str = "") -> Text:
        copy_self = Text(
            plain,
            style=self.style,
            justify=self.justify,
            overflow=self.overflow,
            overflow_side=self._overflow_side,
            overflow_char=self._overflow_char,
            no_wrap=self.no_wrap,
            end=self.end,
            tab_size=self.tab_size,
        )
        return copy_self

    @override
    def copy(self) -> Text:
        copy_self = Text(
            self.plain,
            style=self.style,
            justify=self.justify,
            overflow=self.overflow,
            overflow_side=self._overflow_side,
            overflow_char=self._overflow_char,
            no_wrap=self.no_wrap,
            end=self.end,
            tab_size=self.tab_size,
        )
        copy_self._spans[:] = self._spans  # pylint: disable=protected-access
        return copy_self

    @override
    def truncate(
        self,
        max_width: int,
        *,
        overflow: OverflowMethod | None = None,
        pad: bool = False,
    ) -> None:
        # Matches parent truncate logic except to control side and char.
        _overflow = overflow or self.overflow or DEFAULT_OVERFLOW
        if _overflow != "ignore":
            length = cell_len(self.plain)
            if length > max_width:
                if _overflow == "ellipsis":
                    if self._overflow_side == "right":
                        self.plain = set_cell_size(self.plain, max_width - 1) + self._overflow_char
                    else:
                        self.plain = self._overflow_char + str(set_cell_size(self.plain[::-1], max_width - 1)[::-1])
                else:
                    self.plain = set_cell_size(self.plain, max_width)
            if pad and length < max_width:
                spaces = max_width - length
                self._text = [f"{self.plain}{' ' * spaces}"]
                self._length = len(self.plain)
