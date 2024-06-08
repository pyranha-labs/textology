"""Utilities for routing resource requests based on common URL access patterns."""

from __future__ import annotations

import logging
import re
from functools import total_ordering
from typing import Any
from typing import Callable
from urllib.parse import parse_qs
from urllib.parse import urlparse

from .logging import NullLogger


class Request:
    """User request for a URL."""

    def __init__(
        self,
        url: str,
        method: str = "GET",
    ) -> None:
        """Initialize a user request.

        Args:
            url: Full path to resource requested by user, optionally including parameters and anchors.
            method: Operation method requested from the URL.
        """
        self.method = method
        self.url = urlparse(url)
        self.query = parse_qs(self.url.query)


@total_ordering
class Route:
    """Weighted path for routing, comparing, and collecting variables from user requested paths."""

    def __init__(
        self,
        path: str,
    ) -> None:
        """Initialize route.

        Args:
            path: Base path this route represents when serving user requests.
                Supports "static" paths as /path/1, and "dynamic" paths with variables as /path/{variable_name}.
        """
        self.static_weights: list[list[int]] = []
        self.path: str = path
        self.variables: list[str] = []
        regex = ""
        for index, part in enumerate(path.strip("/").split("/")):
            dynamic_part = part.startswith("{")
            if dynamic_part:
                if not part.endswith("}"):
                    raise ValueError(f"Variable ({part}) missing closing }} in path: {path}")
                var_name = part.strip("{}")
                if var_name in self.variables:
                    raise ValueError(f"Variable ({var_name}) duplicated in path: {path}")
                self.variables.append(var_name)
                regex += rf"/(?P<{var_name}>[^/]+)"
            else:
                self.static_weights.append([index, len(part)])
                regex += f"/{part}"
        self.pattern: re.Pattern = re.compile(rf"^{regex}$")
        self.static: bool = not self.variables

    def __eq__(
        self,
        other: Route,
    ) -> bool:
        """Verify if another route is equal to this route."""
        return self.compare_to(other) == 0

    def __lt__(
        self,
        other: Route,
    ) -> bool:
        """Verify if another route is less than this route."""
        return self.compare_to(other) < 0

    @staticmethod
    def compare_complexity(  # pylint: disable=too-many-return-statements,too-many-branches
        left: Route,
        right: Route,
    ) -> int:
        """Check the complexity of two routes by comparing their static and dynamic parts.

        Less complex routes come before more complex routes.
        A tiered approach is used to compare attributes, stopping at the first unequal comparison.
            1. Static routes sorted by path.
            2. Dynamic routes with more static portions.
            3. Dynamic routes with static portions earlier in the path.
            4. Dynamic routes with shorter static portions.
            5. Dynamic routes with fewer variables.

        Args:
            left: Route to use on the left of comparison operations.
            right: Route to use on the right side of comparison operations.

        Returns:
            -1 if other route is less than this route, 0 if equal, or 1 if greater than.
        """
        if left.static and right.static:
            left_length = len(left.path)
            right_length = len(right.path)
            if left_length > right_length:
                return -1
            if left_length < right_length:
                return 1
            return 0
        if left.static and not right.static:
            return -1
        if not left.static and right.static:
            return 1

        # Both dynamic, check count of static parts.
        left_length = len(left.static_weights)
        right_length = len(right.static_weights)
        if left_length > right_length:
            return -1
        if left_length < right_length:
            return 1

        # Same number of static parts, check position of static parts.
        for left_part, right_part in zip(left.static_weights, right.static_weights):
            if left_part[0] < right_part[0]:
                return -1
            if left_part[0] > right_part[0]:
                return 1
            # Same position of static part, check length of static part.
            if left_part[1] < right_part[1]:
                return -1
            if left_part[1] > right_part[1]:
                return 1
            # Same length of static part, check number of dynamic parts.
            left_length = len(left.variables)
            right_length = len(right.variables)
            if left_length < right_length:
                return -1
            if left_length > right_length:
                return 1
        # Checked entire part stack and could not determine a meaningful difference in complexity.
        return 0

    def compare_to(self, other: Route) -> int:
        """Compare this route to another route using weighted complexity scores.

        Args:
            other: Route to compare to this route.

        Returns:
            -1 if other route is less than this route, 0 if equal, or 1 if greater than.
        """
        return self.compare_complexity(self, other)

    def match(self, path: str) -> bool:
        """Check if the route would match a user path based on regex comparison.

        Args:
            path: User requested path.

        Returns:
            True if the route matches user request, False otherwise.
        """
        return self.pattern.match(path) is not None

    def match_groups(self, path: str) -> dict[str, str]:
        """Collect variables from a user path that matches the route path.

        Args:
            path: User requested path.

        Returns:
            Variables from the route's path/pattern.
        """
        # Trim trailing slashes for consistent endpoints.
        path = path.rstrip("/")
        match = self.pattern.match(path)
        values = match.groupdict() if match else {}
        return values


@total_ordering
class Endpoint:
    """Routing for user requests based on a path/method combo to a callback."""

    def __init__(
        self,
        methods: list[str],
        route: Route | str,
        handler: Callable,
        refresh_allowed: bool = True,
    ) -> None:
        """Initialize endpoint to route requests based on available methods.

        Args:
            methods: Valid operation methods for the route.
                Allows the same path to be registered multiple times, but with different operations.
            route: Route for matching user path requests.
                Also accepts a base path a route represents to create one.
            handler: Where to send user requests when method and route are matched.
            refresh_allowed: Whether refreshes/repeats to this same endpoint are allowed without changing the request.
        """
        self.methods = methods
        self.route = route if isinstance(route, Route) else Route(route)
        self.handler = handler
        self.handler_vars = handler.__code__.co_varnames
        self.refresh_allowed = refresh_allowed

    def __eq__(
        self,
        other: Endpoint,
    ) -> bool:
        """Verify if another endpoint is equal to this endpoint based on routes."""
        return self.route.compare_to(other.route) == 0

    def __lt__(
        self,
        other: Endpoint,
    ) -> bool:
        """Verify if another endpoint is less than this endpoint based on routes."""
        return self.route.compare_to(other.route) < 0


class Router:
    """Routing for path/method requests to matching endpoints.

    Can be used directly as a nested object within an application, or as a "mixin" for an application class. Example:
        router = Router() # Or:
        class RoutedApp(Router):
            ...
        app = RoutedApp()
    """

    def __init__(
        self,
        logger: logging.Logger | None = None,
    ) -> None:
        """Initialize route endpoint trackers and handlers.

        Args:
            logger: Custom logger to send messages to.
        """
        super().__init__()
        self.logger: logging.Logger | None = logger or NullLogger(__name__)
        self.weighted_endpoints: list[Endpoint] = []
        self.dynamic_endpoints: dict[str, dict[str, Endpoint]] = {}  # dynamic_endpoints[path][method]
        self.static_endpoints: dict[str, dict[str, Endpoint]] = {}  # static_endpoints[path][method]
        self.endpoint_not_allowed: Endpoint = Endpoint([], "", self._default_not_allowed_handler)
        self.endpoint_not_found: Endpoint = Endpoint([], "", self._default_not_found_handler)
        self.error_handler: Callable[[Request, BaseException], Any] = self._default_error_handler

    def _add(
        self,
        path: str,
        methods: list[str],
        handler: Callable,
        refresh_allowed: bool = True,
    ) -> Endpoint:
        """Register a function as capable of accepting requests to a specific path/method combo."""
        if not path.startswith("/"):
            raise ValueError(f"Missing required leading slash in path: {path}")
        # Trim trailing slashes for consistent endpoints.
        path = path.rstrip("/")
        methods = [method.upper() for method in methods]
        if "{" not in path and "}" not in path:
            # Add directly to static route map for maximum performance. No custom logic to match inline variables.
            endpoint = self._add_static_route(path, methods, handler, refresh_allowed=refresh_allowed)
        else:
            # Path contains variables, add to weighted method list for performance matching.
            endpoint = self._add_dynamic_route(path, methods, handler, refresh_allowed=refresh_allowed)
        return endpoint

    def _add_dynamic_route(
        self,
        path: str,
        methods: list[str],
        handler: Callable,
        refresh_allowed: bool = True,
    ) -> Endpoint:
        """Register a function as capable of accepting requests with dynamic variables."""
        endpoint = Endpoint(methods, path, handler, refresh_allowed=refresh_allowed)
        # Use pattern instead of path to ensure unique variables are stripped out for consistency.
        pattern = endpoint.route.pattern.pattern
        endpoint_methods = self.dynamic_endpoints.get(pattern, {})
        if pattern not in self.dynamic_endpoints:
            self.dynamic_endpoints[pattern] = endpoint_methods
        for method in methods:
            if method in endpoint_methods:
                raise ValueError(f"Method ({method}) already registered for path: {path}")
            # Add to the weighted list, which is used to path matching.
            self.weighted_endpoints.append(endpoint)
            # Add to the method mapped endpoints, which is used for finding adjacent patterns when one match is found.
            endpoint_methods[method] = endpoint
            self.weighted_endpoints = sorted(self.weighted_endpoints)
            self.logger.debug(f"Registered dynamic route for {method} {path}")
        return endpoint

    def _add_static_route(
        self,
        path: str,
        methods: list[str],
        handler: Callable,
        refresh_allowed: bool = True,
    ) -> Endpoint:
        """Register a function as capable of accepting requests with no dynamic variables."""
        endpoint_methods = self.static_endpoints.get(path, {})
        if path not in self.static_endpoints:
            self.static_endpoints[path] = endpoint_methods
        endpoint = Endpoint(methods, Route(path), handler, refresh_allowed=refresh_allowed)
        for method in methods:
            if method in endpoint_methods:
                raise ValueError(f"Method ({method}) already registered for path: {path}")
            endpoint_methods[method] = endpoint
            self.logger.debug(f"Registered static route for {method} {path}")
        return endpoint

    def _default_error_handler(
        self,
        request: Request,
        error: BaseException,
    ) -> None:
        """Default handler for when all unknown error occur that are not handled elsewhere."""
        if not isinstance(error, Exception):
            # Unhandled fatal error; reraise.
            raise error
        # Show full exception if available to logger, otherwise use standard error logging.
        if hasattr(self.logger, "exception"):
            self.logger.exception(f"Internal Error during {request.method} {request.url.path} {error}")
        else:
            self.logger.error(f"Internal Error during {request.method} {request.url.path} {error}")

    def _default_not_allowed_handler(
        self,
        request: Request,
    ) -> None:
        """Default handler for when a request is made with a method that is not allowed for the endpoint."""
        self.logger.warning(f"Method Not Allowed {request.method} {request.url.path}")

    def _default_not_found_handler(
        self,
        request: Request,
    ) -> None:
        """Default handler for when a request is made to a path that is not found."""
        self.logger.warning(f"Not found {request.url.path}")

    def endpoint(
        self,
        path: str,
        method: str,
    ) -> Endpoint:
        """Find the best endpoint to use with a specific path/method combination.

        Args:
            path: Location of the requested resource.
            method: Operation type to perform on the resource.

        Returns:
            The endpoint registered to the path/method combination if found, or endpoint for missing resources if not.
        """
        # Trim trailing slashes for consistent endpoints.
        path = path.rstrip("/")
        endpoint = self.endpoint_not_found
        # Look in static endpoints first due to performance of exact matches.
        methods = self.static_endpoints.get(path)
        if methods is not None:
            endpoint = methods.get(method) or self.endpoint_not_allowed
        else:
            # Look in dynamic endpoints to see if any match the pattern.
            for weighted_endpoint in self.weighted_endpoints:
                if weighted_endpoint.route.match(path):
                    if method in weighted_endpoint.methods:
                        endpoint = weighted_endpoint
                    else:
                        endpoint = self.dynamic_endpoints.get(weighted_endpoint.route.pattern.pattern, {}).get(
                            method, self.endpoint_not_allowed
                        )
                    break
        return endpoint

    def _get_endpoint_kwargs(
        self,
        endpoint: Endpoint,
        request: Request,
    ) -> dict:
        """Collect dynamic arguments that should be sent to the endpoint based on variables in the handler."""
        kwargs = {}
        if "request" in endpoint.handler_vars:
            kwargs["request"] = request
        return kwargs

    def route(
        self,
        path: str,
        methods: list[str] = ("GET",),
    ) -> Callable:
        """Create a decorator that will register a path/method combination to a callback.

        Example:
            @app.route('/run/{item}')
            def run_item(item: str) -> str:
                ...

        Args:
            path: Resource location that the decorated function will be allowed to respond to.
            methods: One or more methods that the decorated function will be allowed to respond to at the given path.

        Returns:
            A decorator that will register a function as capable of accepting requests to a specific path/method combo.
        """

        def _decorator(func: Callable) -> Callable:
            """Wrapper for calling "add" as a decorator on a function."""
            self._add(path, methods, func)
            return func

        return _decorator

    def serve(
        self,
        url: str,
        method: str = "GET",
    ) -> Any:
        """Serve a user request by matching a path and method against available endpoints.

        Custom serve functions should match this design pattern, but may provide their own "Request" types.
        Unless "endpoint_not_allowed" and "endpoint_not_found" are updated to not require the "request" argument,
        the "request" object must be added to the endpoint kwargs in case a call to the fallback endpoints is required.

        Args:
            url: Full path to request, optionally including parameters and anchors.
            method: Operation type to attempt against the path.

        Returns:
            The result of handling the request.
        """
        request = Request(url, method=method)
        path = request.url.path
        endpoint = self.endpoint(path, method)
        result = None
        self.logger.debug(f"Serving new request: {method} {url}")
        try:
            kwargs = self._get_endpoint_kwargs(endpoint, request)
            if not endpoint.route.static:
                kwargs.update(**endpoint.route.match_groups(path))
            result = endpoint.handler(**kwargs)
        except BaseException as base_error:  # pylint: disable=broad-exception-caught
            # Catch all errors to allow preventing fatal crashes in server loops during the error handler.
            try:
                result = self.error_handler(  # Overrides can return a value. pylint: disable=assignment-from-no-return
                    request, base_error
                )
            except Exception as error:  # pylint: disable=broad-exception-caught
                self.logger.error(f"Failed to handle error with error handler {method} {request.url.path} {error}")
        return result
