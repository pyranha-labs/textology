"""Unit tests for pages module."""

from typing import Callable

import pytest

from textology import pages


def home() -> None:
    """Fake layout function that does not have the "layout_" prefix."""


def layout_home() -> None:
    """Fake layout function that has the "layout_" prefix."""


def layout_home_page() -> None:
    """Fake layout function that has the "layout_"  prefix and a suffix with underscore."""


TEST_CASES = {
    "Page": {
        "layout only, with prefix": {
            "args": [
                layout_home,
            ],
            "attributes": {
                "path": "/home",
                "name": "Home",
            },
        },
        "layout only, without prefix": {
            "args": [
                home,
            ],
            "attributes": {
                "path": "/home",
                "name": "Home",
            },
        },
        "layout only, with prefix and suffix": {
            "args": [
                layout_home_page,
            ],
            "attributes": {
                "path": "/home_page",
                "name": "Home Page",
            },
        },
        "layout and path, no leading slash": {
            "args": [
                layout_home,
            ],
            "kwargs": {
                "path": "casa",
            },
            "attributes": {
                "path": "/casa",
                "name": "Casa",
            },
        },
    },
}


@pytest.mark.parametrize(
    "test_case",
    list(TEST_CASES["Page"].values()),
    ids=list(TEST_CASES["Page"].keys()),
)
def test_page_init(test_case: dict, function_tester: Callable) -> None:
    """Test that page initializes with explicit values or automatically populated values."""
    function_tester(test_case, pages.Page)
