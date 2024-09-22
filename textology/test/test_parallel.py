"""Unit tests for parallel module."""

import time
from typing import Any
from typing import Callable

import pytest

from textology import parallel


def _task_with_args(first: int, second: int, sleep: int = 0) -> int:
    """Return a value while using input arguments."""
    if sleep:
        time.sleep(sleep)
    return first + second


def _task_without_args() -> int:
    """Return a value without using any input arguments."""
    return 123


TEST_CASES = {
    "parallelize": {
        "unordered": {
            "args": [
                [_task_with_args] * 2,
            ],
            "kwargs": {
                "func_args": [
                    (1, 2),
                    (2, 3),
                ],
                "func_kwargs": [
                    {"sleep": 2},
                    {"sleep": 1},
                ],
                "with_index": True,
            },
            "returns": [
                (1, 5),
                (0, 3),
            ],
        },
        "ordered": {
            "args": [
                [_task_with_args] * 2,
            ],
            "kwargs": {
                "func_args": [
                    (1, 2),
                    (2, 3),
                ],
                "func_kwargs": [
                    {"sleep": 2},
                    {"sleep": 1},
                ],
                "ordered": True,
                "with_index": True,
            },
            "returns": [
                (0, 3),
                (1, 5),
            ],
        },
        "no index": {
            "args": [
                [_task_with_args] * 2,
            ],
            "kwargs": {
                "ordered": True,
                "func_args": [
                    (1, 2),
                    (2, 3),
                ],
            },
            "returns": [
                3,
                5,
            ],
        },
        "no func args": {
            "args": [
                [_task_without_args] * 2,
            ],
            "kwargs": {
                "ordered": True,
                "with_index": True,
            },
            "returns": [
                (0, 123),
                (1, 123),
            ],
        },
        "no threads": {
            "args": [
                [_task_without_args] * 2,
            ],
            "kwargs": {
                "use_threads": False,
                "mp_context": "spawn",
                "ordered": True,
                "with_index": True,
            },
            "returns": [
                (0, 123),
                (1, 123),
            ],
        },
        "error in one function, with raise": {
            "args": [
                [_task_with_args] * 2,
            ],
            "kwargs": {
                "func_args": [
                    (1, 2),
                    ("2", 3),
                ],
                "ordered": True,
                "with_index": True,
            },
            "raises": TypeError,
        },
        "error, without raise": {
            "args": [
                [_task_with_args] * 2,
            ],
            "kwargs": {
                "func_args": [
                    (1, 2),
                    ("2", 3),
                ],
                "ordered": True,
                "with_index": True,
                "exit_on_error": False,
            },
            "returns": [
                (0, 3),
                (1, 'TypeError(can only concatenate str (not "int") to str)'),
            ],
        },
        "args too short": {
            "args": [
                [_task_with_args] * 2,
            ],
            "kwargs": {
                "func_args": [
                    (1, 2),
                ],
            },
            "raises": ValueError,
        },
        "kwargs too short": {
            "args": [
                [_task_with_args] * 2,
            ],
            "kwargs": {
                "func_args": [
                    (1, 2),
                    (2, 3),
                ],
                "func_kwargs": [
                    {"sleep": 1},
                ],
            },
            "raises": ValueError,
        },
    },
}


@pytest.mark.parametrize_test_case("test_case", TEST_CASES["parallelize"])
def test_parallelize(test_case: dict, function_tester: Callable) -> None:
    """Test that parallelize will run with various argument combinations."""

    def _parallelize(*args: Any, **kwargs: Any) -> list:
        results = [result for result in parallel.parallelize(*args, **kwargs)]
        for index, result in enumerate(results):
            if isinstance(result, tuple):
                if isinstance(result[1], BaseException):
                    results[index] = (result[0], f"{result[1].__class__.__name__}({result[1]})")
            else:
                if isinstance(result, BaseException):
                    results[index] = f"{result.__class__.__name__}({result})"
        return results

    function_tester(test_case, _parallelize)


def test_parallel_pool_executor_extras() -> None:
    """Test the misc scenarios of ParallelPoolExecutor not covered by testing 'parallelize'."""
    results = []
    with parallel.ParallelPoolExecutor() as pool:
        # Test the following misc scenarios:
        # - Multiple, separate, submits.
        # - Submit with single function/arguments.
        # - Call to as_completed after completed.
        pool.submit([_task_with_args] * 2, func_args=[(1, 2), (2, 3)], func_kwargs=[{"sleep": 3}, {"sleep": 2}])
        assert pool.submitted == 2
        pool.submit(_task_with_args, func_args=(3, 4), func_kwargs={"sleep": 1})
        assert pool.submitted == 3
        for result in pool.as_completed(ordered=True, with_index=True):
            results.append(result)
        assert pool.completed == 3
        for result in pool.as_completed():
            results.append(result)
    assert results == [
        (0, 3),
        (1, 5),
        (2, 7),
    ]
