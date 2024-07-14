"""Container widget used for routing paged content."""

from typing import Any
from typing import Iterable

from textual.events import Message
from textual.reactive import reactive

from . import Callback
from . import Container
from . import Widget


class PageContainer(Container):
    """Container used to display page contents, and signal to multi-page applications which ID to use in callbacks.

    If not used in a multi-page app, it is functionally the same as a Container. It also contains attributes and logic
    similar to a ContentSwitcher.
    """

    page: str | None = reactive(None, repaint=False, init=False)

    def __init__(
        self,
        *children: Widget,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        styles: dict[str, Any] | None = None,
        disabled_messages: Iterable[type[Message]] | None = None,
        callbacks: dict[str, Callback] | None = None,
    ) -> None:
        """Initialize the paged container with initial children and additional tracking.

        Args:
            *children: Child widgets.
            name: The name of the widget.
            id: The ID of the widget in the DOM.
            classes: The CSS classes for the widget.
            disabled: Whether the widget is disabled or not.
            styles: Local inline styles to apply on top of the class' styles for only this instance.
            disabled_messages: List of messages to disable on this widget instance only.
            callbacks: Mapping of callbacks to send messages to instead of sending to default handler.
        """
        super().__init__(
            *children,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
            styles=styles,
            disabled_messages=disabled_messages,
            callbacks=callbacks,
        )
        self._page_cache: dict[str, Widget] = {}

    async def add_page(self, page: str, content: Widget) -> None:
        """Add a page to the cache.

        Args:
            page: Name of the page to use during cache requests.
            content: Content to display when the current page is updated.
        """
        with self.app.batch_update():
            if page in self._page_cache:
                await self._page_cache.pop(page).remove()
            content.display = False
            await self.mount(content)
        self._page_cache[page] = content
        if not self.page:
            self.page = page

    def is_cached(self, page: str) -> bool:
        """Check whether the container has the request page in the cache.

        Return:
            True if the page is found in the cache, False otherwise.
        """
        return page in self._page_cache

    async def remove_page(self, page: str) -> None:
        """Remove a page from the cache."""
        with self.app.batch_update():
            if page in self._page_cache:
                await self._page_cache.pop(page).remove()
        if self.page == page:
            self.page = None

    def watch_page(self, old: str | None, new: str | None) -> None:
        """React to the current visible child choice being changed.

        Args:
            old: The old path that was displayed.
            new: The new path to be shown.
        """
        with self.app.batch_update():
            if old_widget := self._page_cache.get(old):
                old_widget.display = False
            if new_widget := self._page_cache.get(new):
                new_widget.display = True
