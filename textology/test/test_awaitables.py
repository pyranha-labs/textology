"""Unit tests for awaitables module."""

import threading

from textology import awaitables


def test_await_complete_or_noop_thread() -> None:
    """Test that AwaitCompleteOrNoop initializes when in a thread without an async loop."""

    def _thread() -> awaitables.AwaitCompleteOrNoop:
        return awaitables.AwaitCompleteOrNoop()

    # Test creation from primary thread.
    _thread()

    # Test creation in non-primary thread, which would normally crash async object creation.
    thread = threading.Thread(target=_thread)
    thread.start()
    thread.join()
