"""Global fixtures for pytest."""

import asyncio
import inspect
from concurrent.futures import ThreadPoolExecutor
from types import GeneratorType
from typing import Any
from typing import Callable
from typing import Coroutine

import pytest

pytest_plugins = ("textology.pytest_utils",)


@pytest.fixture
def function_tester() -> Callable[[dict, Callable, Callable | None, bool, pytest.MonkeyPatch | None], None]:
    """Create a reusable fixture to run a basic test case against a function."""

    def function_tester(
        test: dict,
        func: Callable,
        compare: Callable[[Any, Any], None] | None = None,
        drain: bool = True,
        monkeypatch: pytest.MonkeyPatch | None = None,
    ) -> None:
        """Run a basic test case against a function.

        Test case guidelines:
            - If testing function output, use: args and/or kwargs + returns
            - If testing function exceptions, use: args and/or kwargs + raises
            - If testing class creation, use class' __call__ in the test, and use: args and/or kwargs + attributes
            - If testing patched functions, use: patches with a list of target, name, value matching monkeypatch input.

        Args:
            test: Configuration parameters for testing a callable.
                Optional keys: "args" and/or "kwargs"
                Mandatory keys: "returns" or "raises" or "attributes"
            func: A callable to pass args and kwargs to, and capture results/errors from.
            compare: A function to use for comparing the actual result and expected result.
                Defaults to a "==" comparison.
            drain: Whether to convert generator results into lists.
            monkeypatch: Optional pytest monkeypatch fixture to use for temporary patches via "patches"
        """
        args, kwargs, raises, patches = _initialize_test(test)
        if patches and monkeypatch:
            for patch in patches:
                _patch_test(*patch, monkeypatch=monkeypatch)
        if raises:
            with pytest.raises(raises):
                result = _execute_test(func, *args, **kwargs)
                if drain and isinstance(result, GeneratorType):
                    list(result)
        else:
            result = _execute_test(func, *args, **kwargs)
            if drain and isinstance(result, GeneratorType):
                result = list(result)
            _finalize_test(test, result, compare)

    return function_tester


def _initialize_test(test: dict) -> tuple[list, dict, type[BaseException] | None, list[tuple] | None]:
    """Pull out the primary arguments for running a test."""
    result_types_found = [name in test for name in ("returns", "raises", "attributes")]
    if not result_types_found.count(True):
        raise ValueError("Test must declare one of: returns, raises, attributes")
    if result_types_found.count(True) > 1:
        raise ValueError("Test must declare only one of: returns, raises, attributes")
    return test.get("args", []), test.get("kwargs", {}), test.get("raises"), test.get("patches")


def _execute_test(func: Callable | Coroutine, *args: Any, **kwargs: Any) -> Any:
    """Run a function, or coroutine, safely in pytest and return the result."""
    # A custom executor must be used to convert async to sync. A new loop cannot be created from the main thread,
    # and the pytest event loop will not allow new tasks to be run directly.
    if asyncio.iscoroutinefunction(func):
        with ThreadPoolExecutor(1) as pool:
            result = pool.submit(lambda: asyncio.run(func(*args, **kwargs))).result()
    else:
        result = func(*args, **kwargs)
        # If the result of a sync function is an async future, discard and try again with as a full coroutine.
        if inspect.isawaitable(result):

            async def _run_in_thread() -> Any:
                """Create an awaitable function from a non-async function."""
                return await func(*args, **kwargs)

            result = _execute_test(_run_in_thread)
    return result


def _finalize_test(test: dict, result: Any, compare: Callable[[Any, Any], None] | None) -> None:
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


def _patch_test(target: Any, name: str, value: Callable, monkeypatch: pytest.MonkeyPatch) -> None:
    """Apply a temporary monkeypatch while a test is running."""
    original = getattr(target, name)
    if inspect.isfunction(original):
        # Allow patching with or without an async method, such as with a lambda.
        if asyncio.iscoroutinefunction(original) and not asyncio.iscoroutinefunction(value):

            async def _func(*args: Any, **kwargs: Any) -> Any:
                """Asynchronously run the patched function for feature parity."""
                result = value(*args, **kwargs)
                if asyncio.iscoroutine(result):
                    result = await result
                return result
        else:
            _func = value

        # Allow lambdas to be used as patches for class and static methods.
        attr = inspect.getattr_static(target, name)
        if isinstance(attr, staticmethod) and not isinstance(_func, staticmethod):
            _func = staticmethod(_func)
        elif isinstance(attr, classmethod) and not isinstance(_func, classmethod):
            _func = classmethod(_func)

        monkeypatch.setattr(target, name, _func)
    else:
        monkeypatch.setattr(target, name, value)


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
