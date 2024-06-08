"""Unit tests for router module."""

from typing import Callable

import pytest

from textology import router

test_default_router = router.Router()
test_router = router.Router()


TEST_CASES = {
    "Route init": {
        "missing dynamic bracket": {
            "args": ["/test/{value"],
            "raises": ValueError,
        },
        "duplicate dynamic name": {
            "args": ["/test/{value}/{value}"],
            "raises": ValueError,
        },
    },
    "Route compare_complexity": {
        "equal": {
            "args": [
                router.Route("/test"),
                router.Route("/test"),
            ],
            "returns": 0,
        },
        "left more specific, both static": {
            "args": [
                router.Route("/test1"),
                router.Route("/test"),
            ],
            "returns": -1,
        },
        "right more specific, both static": {
            "args": [
                router.Route("/test"),
                router.Route("/test2"),
            ],
            "returns": 1,
        },
        "left static": {
            "args": [
                router.Route("/test"),
                router.Route("/test/{value}"),
            ],
            "returns": -1,
        },
        "right static": {
            "args": [
                router.Route("/test/{value}"),
                router.Route("/test"),
            ],
            "returns": 1,
        },
        "both dynamic, left more static weights": {
            "args": [
                router.Route("/test/category/{value}"),
                router.Route("/test/{value}"),
            ],
            "returns": -1,
        },
        "both dynamic, right more static weights": {
            "args": [
                router.Route("/test/{value}"),
                router.Route("/test/category/{value}"),
            ],
            "returns": 1,
        },
        "both dynamic, multiple static, left earlier": {
            "args": [
                router.Route("/test/value/{category}"),
                router.Route("/test/{category}/value"),
            ],
            "returns": -1,
        },
        "both dynamic, multiple static, right earlier": {
            "args": [
                router.Route("/test/{category}/value"),
                router.Route("/test/value/{category}"),
            ],
            "returns": 1,
        },
        "both dynamic, multiple static, left longer": {
            "args": [
                router.Route("/test/values/{value}"),
                router.Route("/test/value/{value}"),
            ],
            "returns": 1,
        },
        "both dynamic, multiple static, right longer": {
            "args": [
                router.Route("/test/value/{value}"),
                router.Route("/test/values/{value}"),
            ],
            "returns": -1,
        },
        "both dynamic, multiple static and dynamic, left more dynamic": {
            "args": [
                router.Route("/test/values/{value}/{subvalue}"),
                router.Route("/test/values/{value}"),
            ],
            "returns": 1,
        },
        "both dynamic, multiple static and dynamic, right more dynamic": {
            "args": [
                router.Route("/test/values/{value}"),
                router.Route("/test/values/{value}/{subvalue}"),
            ],
            "returns": -1,
        },
        "both dynamic, multiple static and dynamic, no meaningful difference": {
            "args": [
                router.Route("/test/foo/{value}/{subvalue}"),
                router.Route("/test/bar/{value}/{subvalue}"),
            ],
            "returns": 0,
        },
    },
    "Router serve": {
        "static": {
            "args": [test_router, "/test"],
            "returns": "default",
        },
        "dynamic": {
            "args": [test_router, "/test/myvalue"],
            "returns": "myvalue",
        },
        "error": {
            "args": [test_router, "/raises"],
            "returns": "ValueError bad stuff",
        },
        "low level error": {
            "args": [test_router, "/raises-exit"],
            "returns": "SystemExit really bad stuff",
        },
        "not allowed": {
            "args": [test_router, "/test", "POST"],
            "returns": "POST /test not allowed",
        },
        "not found": {
            "args": [test_router, "/notfound", "GET"],
            "returns": "GET /notfound not found",
        },
        "error, default": {
            "args": [test_default_router, "/raises"],
            "returns": None,
        },
        "low level error, default": {
            "args": [test_default_router, "/raises-exit"],
            "raises": SystemExit,
        },
        "not allowed, default": {
            "args": [test_default_router, "/test", "POST"],
            "returns": None,
        },
        "not found, default": {
            "args": [test_default_router, "/notfound", "GET"],
            "returns": None,
        },
    },
}


def __mock_error_handler__(
    request: router.Request,
    error: BaseException,
) -> str:
    return f"{type(error).__name__} {error}"


def __mock_not_allowed_handler__(
    request: router.Request,
) -> str:
    return f"{request.method} {request.url.path} not allowed"


def __mock_not_found_handler__(
    request: router.Request,
) -> str:
    return f"{request.method} {request.url.path} not found"


test_router.error_handler = __mock_error_handler__
test_router.endpoint_not_allowed = router.Endpoint([], "", __mock_not_allowed_handler__)
test_router.endpoint_not_found = router.Endpoint([], "", __mock_not_found_handler__)


@test_default_router.route("/test")
@test_router.route("/test")
def _route() -> str:
    return "default"


@test_default_router.route("/test/{arg}")
@test_router.route("/test/{arg}")
def _route_with_arg(arg: str) -> str:
    return arg


@test_default_router.route("/raises")
@test_router.route("/raises")
def _route_with_raise() -> str:
    raise ValueError("bad stuff")


@test_default_router.route("/raises-exit")
@test_router.route("/raises-exit")
def _route_with_raise() -> str:
    raise SystemExit("really bad stuff")


@pytest.mark.parametrize_test_case("test_case", TEST_CASES["Route compare_complexity"])
def test_route_compare_complexity(test_case: dict, function_tester: Callable) -> None:
    """Test route comparisons."""
    function_tester(test_case, router.Route.compare_complexity)


@pytest.mark.parametrize_test_case("test_case", TEST_CASES["Route init"])
def test_route_init(test_case: dict, function_tester: Callable) -> None:
    """Test route initializations."""
    function_tester(test_case, router.Route)


@pytest.mark.parametrize_test_case("test_case", TEST_CASES["Router serve"])
def test_router_serve(test_case: dict, function_tester: Callable) -> None:
    """Test router serve result."""
    function_tester(test_case, router.Router.serve)
