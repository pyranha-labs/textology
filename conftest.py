"""Global fixtures for pytest."""

from types import GeneratorType
from typing import Any
from typing import Awaitable
from typing import Callable

import pytest
import pytest_asyncio

pytest_plugins = ("textology.pytest_utils",)


@pytest_asyncio.fixture(name="async_function_tester")
def async_function_tester() -> Callable[[dict, Callable, Callable, bool], Awaitable]:
    """Create a reusable fixture to run a basic test case against an async function."""

    async def async_function_tester(
        test: dict,
        func: Callable,
        compare: Callable[[Any, Any], None] | None = None,
        drain: bool = True,
    ) -> None:
        """Run a basic test case against an async function.

        Test case guidelines:
            - If testing function output, use: args and/or kwargs + returns
            - If testing function exceptions, use: args and/or kwargs + raises
            - If testing class creation, use class' __call__ in the test, and use: args and/or kwargs + attributes

        Args:
            test: Configuration parameters for testing a callable.
                Optional keys: "args" and/or "kwargs"
                Mandatory keys: "returns" or "raises" or "attributes"
            func: An async callable to pass args and kwargs to, and capture results/errors from.
            compare: A function to use for comparing the actual result and expected result.
                Defaults to a "==" comparison.
            drain: Whether to convert generator results into lists.
        """
        args, kwargs, raises = _init_tester(test)
        if raises:
            with pytest.raises(raises):
                result = await func(*args, **kwargs)
                if drain and isinstance(result, GeneratorType):
                    list(result)
        else:
            result = await func(*args, **kwargs)
            if drain and isinstance(result, GeneratorType):
                result = list(result)
            _finish_tester(test, result, compare)

    return async_function_tester


@pytest.fixture
def function_tester() -> Callable[[dict, Callable, Callable, bool], None]:
    """Create a reusable fixture to run a basic test case against a function."""

    def function_tester(
        test: dict,
        func: Callable,
        compare: Callable[[Any, Any], None] | None = None,
        drain: bool = True,
    ) -> None:
        """Run a basic test case against a function.

        Test case guidelines:
            - If testing function output, use: args and/or kwargs + returns
            - If testing function exceptions, use: args and/or kwargs + raises
            - If testing class creation, use class' __call__ in the test, and use: args and/or kwargs + attributes

        Args:
            test: Configuration parameters for testing a callable.
                Optional keys: "args" and/or "kwargs"
                Mandatory keys: "returns" or "raises" or "attributes"
            func: A callable to pass args and kwargs to, and capture results/errors from.
            compare: A function to use for comparing the actual result and expected result.
                Defaults to a "==" comparison.
            drain: Whether to convert generator results into lists.
        """
        args, kwargs, raises = _init_tester(test)
        if raises:
            with pytest.raises(raises):
                result = func(*args, **kwargs)
                if drain and isinstance(result, GeneratorType):
                    list(result)
        else:
            result = func(*args, **kwargs)
            if drain and isinstance(result, GeneratorType):
                result = list(result)
            _finish_tester(test, result, compare)

    return function_tester


def _init_tester(test: dict) -> tuple[list, dict, type[BaseException] | None]:
    """Pull out the primary arguments for running a test."""
    result_types_found = [name in test for name in ("returns", "raises", "attributes")]
    if not result_types_found.count(True):
        raise ValueError("Test must declare one of: returns, raises, attributes")
    if result_types_found.count(True) > 1:
        raise ValueError("Test must declare only one of: returns, raises, attributes")
    return test.get("args", []), test.get("kwargs", {}), test.get("raises")


def _finish_tester(test: dict, result: Any, compare: Callable[[Any, Any], None] | None) -> None:
    """Validate the results of running a test."""
    expected = test.get("returns")
    attributes = test.get("attributes")
    if attributes is not None and not attributes:
        raise ValueError("Test attributes result type must have values")
    if attributes:
        attribute_results = {name: getattr(result, name) for name in attributes.keys()}
        equals = compare(attribute_results, attributes) if compare else attribute_results == attributes
        assert equals, f"\nResult:\n\t{attribute_results}\nExpected:\n\t{attributes}"
    else:
        equals = compare(result, expected) if compare else expected == result
        assert equals, f"\nResult:\n\t{result}\nExpected:\n\t{expected}"


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    """Process custom paramtrize options to streamline sets of tests with easily identifiable ids."""
    mark = metafunc.definition.get_closest_marker("parametrize_test_case")
    if mark:
        args = list(mark.args)
        test_case = args[1]
        args[1] = [value for value in (list(test_case.values()) if isinstance(test_case, dict) else test_case)]
        kwargs = mark.kwargs
        kwargs["ids"] = [str(value) for value in (list(test_case.keys()) if isinstance(test_case, dict) else test_case)]
        metafunc.parametrize(*args, **kwargs)
