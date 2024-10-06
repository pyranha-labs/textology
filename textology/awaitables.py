"""Utilities for working with awaitable objects returned by async methods."""

from __future__ import annotations

import asyncio
from typing import Any
from typing import Awaitable
from typing import Callable
from typing import Generator

import rich.repr
from textual.message_pump import MessagePump

Runnable = Awaitable | Callable[[], Awaitable | Any] | None


@rich.repr.auto(angular=True)
class AwaitCompleteOrNoop:
    """An 'optionally-awaitable' object which runs coroutines (or other awaitables) concurrently, or exits immediately.

    Functionally equivalent to `textual.await_complete.AwaitComplete`, but can be instantiated without an async loop
    if there is nothing to await. This ensures that the result provides a consistent interface, whether there
    are async tasks to complete or not.

    If there are awaitables, this must be called from within an async loop.
    """

    def __init__(self, *awaitables: Awaitable) -> None:
        """Initialize an AwaitCompleteOrNoop.

        Args:
            awaitables: Optional awaitables to run concurrently. If none are provided, this will act as a no-op.
        """
        if awaitables:
            self._future = gather(*awaitables)
        else:
            self._future = None

    def __await__(self) -> Generator[Any, None, Any]:
        """Wait for the tasks to complete, or return immediately if no tasks."""
        if not self._future:
            yield None
            return None
        return self._future.__await__()

    async def __call__(self) -> Any:
        """Wait for the tasks to complete, or return immediately if no tasks."""
        return await self

    def call_next(self, node: MessagePump) -> AwaitCompleteOrNoop:
        """Await after the next message.

        Args:
            node: The node which created the object.
        """
        node.call_next(self)
        return self

    @property
    def is_done(self) -> bool:
        """True if the task has completed or there was no task."""
        if not self._future:
            return True
        return self._future.done()

    @property
    def exception(self) -> BaseException | None:
        """The exception raised if the awaitables failed, or None if all succeeded (or no task)."""
        if not self._future:
            return None
        return self._future.exception() if self.is_done else None


def gather(*aws: Runnable, return_exceptions: bool = True) -> asyncio.Future:
    """Return a future aggregating results from the given functions/coroutines/futures.

    Args:
        aws: Awaitables, or functions to wrap in awaitables, to run concurrently.
        return_exceptions: Whether to raise exceptions, or return as results.

    Returns:
        A future aggregating all the results from the given functions/coroutines/futures.
    """
    results = []
    for awaitable in aws:
        if asyncio.iscoroutinefunction(awaitable):
            results.append(awaitable())
        elif asyncio.iscoroutine(awaitable):
            results.append(awaitable)
        else:
            results.append(_make_awaitable(awaitable)())
    return asyncio.gather(*results, return_exceptions=return_exceptions)


def _make_awaitable(func: Callable) -> Any:
    """Create an awaitable function from a non-async function."""

    async def _awaitable() -> Any:
        return func()

    return _awaitable
