"""Unit tests for awaitables module."""

import threading
from typing import Callable

import pytest

from textology import awaitables

TEST_CASES = {
    "gather": {
        "no async": {
            "args": [
                lambda: 123,
                lambda: 456,
                lambda: 789,
            ],
            "returns": [
                123,
                456,
                789,
            ],
        },
        "all async": {
            "args": [
                awaitables._make_awaitable(lambda: 123),
                awaitables._make_awaitable(lambda: 456),
                awaitables._make_awaitable(lambda: 789),
            ],
            "returns": [
                123,
                456,
                789,
            ],
        },
        "mix": {
            "args": [
                lambda: 123,
                awaitables._make_awaitable(lambda: 456),
                lambda: 789,
                awaitables._make_awaitable(lambda: 0),
            ],
            "returns": [
                123,
                456,
                789,
                0,
            ],
        },
    },
}


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


@pytest.mark.parametrize_test_case("test_case", TEST_CASES["gather"])
def test_gather(test_case: dict, function_tester: Callable) -> None:
    """Test that gather returns the expected results."""
    function_tester(test_case, awaitables.gather)
