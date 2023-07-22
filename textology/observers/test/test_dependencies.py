"""Unit tests for observers dependency module."""

from typing import Callable

import pytest

from textology.observers import Dependency
from textology.observers import Modified
from textology.observers import Published
from textology.observers import Raised
from textology.observers import Select
from textology.observers import Update
from textology.observers._dependencies import validate_dependencies


class ComponentWithID:
    """Basic example of a component object that is compatible with SupportsID."""

    def __init__(self, id: str) -> None:
        """Initialize component with an id for searching."""
        super().__init__()
        self.id = id


class ComponentWithoutID:
    """Basic example of a component object that is not compatible with SupportsID."""

    def __init__(self, value: str) -> None:
        """Initialize component with an id for searching."""
        super().__init__()
        self.value = value


class FakeEvent:
    """Basic example of an event class."""


TEST_CASES = {
    "Dependency init": {
        "valid string": {
            "args": ["id", "property"],
            "attributes": {
                "component_id": "id",
                "component_property": "property",
            },
        },
        "valid object": {
            "args": [ComponentWithID("id"), "property"],
            "attributes": {
                "component_id": "id",
                "component_property": "property",
            },
        },
        "invalid object, no ID": {
            "args": [ComponentWithoutID("value"), "property"],
            "raises": AttributeError,
        },
    },
    "Published init": {
        "valid object": {
            "args": ["id", FakeEvent],
            "attributes": {
                "component_id": "id",
                "component_property": "test_dependencies.FakeEvent",
            },
        },
        "invalid string": {
            "args": ["id", "property"],
            "raises": AttributeError,
        },
    },
    "validate_dependencies": {
        "valid input output property combo": {
            "args": [
                Modified("id", "property"),
                Update("id", "property"),
            ],
            "returns": None,
        },
        "valid input output event combo": {
            "args": [
                Published("id", FakeEvent),
                Update("id", "property"),
            ],
            "returns": None,
        },
        "valid input output exception combo": {
            "args": [
                Raised(ValueError),
                Update("id", "property"),
            ],
            "returns": None,
        },
        "valid property input only": {
            "args": [
                Modified("id", "property"),
            ],
            "returns": None,
        },
        "valid event input only": {
            "args": [
                Published("id", FakeEvent),
            ],
            "returns": None,
        },
        "valid exception input only": {
            "args": [
                Raised(ValueError),
            ],
            "returns": None,
        },
        "valid exception and other non-triggering input": {
            "args": [
                Raised(ValueError),
                Select("id", "property"),
                Update("id", "property"),
            ],
            "raises": None,
        },
        "duplicate inputs": {
            "args": [
                Modified("id", "property"),
                Modified("id", "property"),
                Update("id", "property"),
            ],
            "raises": ValueError,
        },
        "no inputs": {
            "args": [
                Select("id", "property"),
                Update("id", "property"),
            ],
            "raises": ValueError,
        },
        "invalid exception and other triggering input": {
            "args": [
                Raised(ValueError),
                Modified("id", "property"),
                Update("id", "property"),
            ],
            "raises": ValueError,
        },
    },
}


@pytest.mark.parametrize(
    "test_case",
    list(TEST_CASES["Dependency init"].values()),
    ids=list(TEST_CASES["Dependency init"].keys()),
)
def test_dependency_init(test_case: dict, function_tester: Callable) -> None:
    """Test that a generic dependency can be initialized with provided values."""
    function_tester(test_case, Dependency.__call__)


@pytest.mark.parametrize(
    "test_case",
    list(TEST_CASES["Published init"].values()),
    ids=list(TEST_CASES["Published init"].keys()),
)
def test_published_init(test_case: dict, function_tester: Callable) -> None:
    """Test that a Published dependency can be initialized with provided values."""
    function_tester(test_case, Published.__call__)


@pytest.mark.parametrize(
    "test_case",
    list(TEST_CASES["validate_dependencies"].values()),
    ids=list(TEST_CASES["validate_dependencies"].keys()),
)
def test_validate_dependencies(test_case: dict, function_tester: Callable) -> None:
    """Test that validate_dependencies detect incorrect configurations."""
    function_tester(test_case, validate_dependencies)
