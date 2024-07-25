"""Container widget used for routing paged content."""

from typing import Any
from typing import Iterable

from textual.events import Message
from textual.events import Mount
from textual.reactive import reactive

from textology.awaitables import AwaitCompleteOrNoop

from . import Callbacks
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
        *children: Widget | tuple[str, Widget],
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        styles: dict[str, Any] | None = None,
        disabled_messages: Iterable[type[Message]] | None = None,
        callbacks: Callbacks | None = None,
    ) -> None:
        """Initialize the paged container with initial children and additional tracking.

        Args:
            *children: Child widgets, or tuples of page names and child widgets to cache.
            name: The name of the widget.
            id: The ID of the widget in the DOM.
            classes: The CSS classes for the widget.
            disabled: Whether the widget is disabled or not.
            styles: Local inline styles to apply on top of the class' styles for only this instance.
            disabled_messages: List of messages to disable on this widget instance only.
            callbacks: Mapping of callbacks to send messages to instead of sending to default handler.
        """
        self._page_cache: dict[str, Widget] = {}
        self._pending_mount: list[Widget] = []
        new_children = []
        for child in children:
            if isinstance(child, tuple):
                page, child = child
                self._page_cache[page] = child
                new_children.append(child)
        super().__init__(
            *new_children,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
            styles=styles,
            disabled_messages=disabled_messages,
            callbacks=callbacks,
        )

    def add_page(self, page: str, content: Widget, show_first: bool = True) -> AwaitCompleteOrNoop:
        """Add a page to the cache.

        Args:
            page: Name of the page to use during cache requests.
            content: Content to display when the current page is updated.
            show_first: Mark the first page added as visible if no page is currently visible.

        Returns:
            Optionally awaitable event that completes after new page is mounted.
            If called before the widget is mounted, this is a noop, and Page is mounted after widget mounts.
        """
        with self.app.batch_update():
            content.display = False
            old_page = None
            if page in self._page_cache:
                old_page = self._page_cache.pop(page)
        self._page_cache[page] = content
        if show_first and not self.page:
            self.page = page

        if self.is_mounted:

            async def _mount() -> None:
                """Swap the old page if applicable, and mount the new page."""
                with self.app.batch_update():
                    if old_page:
                        await old_page.remove()
                    await self.mount(content)

            await_complete = AwaitCompleteOrNoop(_mount())
        else:
            await_complete = AwaitCompleteOrNoop()
            self._pending_mount.append(content)

        self.call_next(await_complete)
        return await_complete

    def is_cached(self, page: str) -> bool:
        """Check whether the container has the request page in the cache.

        Return:
            True if the page is found in the cache, False otherwise.
        """
        return page in self._page_cache

    async def on_mount(self, _: Mount) -> None:
        """Mount any pending children that could not be mounted during page adds."""
        if self._pending_mount:
            self.mount_all(self._pending_mount)

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
