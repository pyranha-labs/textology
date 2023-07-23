"""Dash compatibility layer for creating Textual applications in "Plotly Dash" code style.

The goal of this library is to provide a familiar interface for developers who have worked with Plotly Dash
to make UI web applications, due to usage of similar principles. This can be used for most applications,
or to help transition developers to the style used in Textology for "observation pattern" type applications.

While this library provides compatibility across frameworks in style where possible, it is not a guarantee or promise
for any specific features or functionality. If a feature in Textology extended applications has an equivalent in Dash,
it will be included here, but this is not Dash. In order to access the full range of Textology and Textual features,
developers may need to leverage the native classes and designs from the base libraries.
"""

from typing import Callable

from .apps import ExtendedApp

# Compatibility aliases for Dash.
# Allow importing other modules for direct access through this module for simplicity. pylint: disable=unused-import
from .observers import Dependency
from .observers import Modified
from .observers import NoUpdate
from .observers import Published
from .observers import Raised
from .observers import Select as State
from .observers import SupportsID
from .observers import Update as Output
from .observers import when as callback

InputType = Modified | Published | Raised


class DashCompatApp(ExtendedApp):
    """Application capable of performing automatic input/output callbacks on reactive widget property updates.

    Compatibility alias for ExtendedApp class.
    """

    def callback(
        self,
        *dependencies: Dependency,
    ) -> Callable:
        """Register a callback that triggers when observed values change.

        Compatibility alias for ExtendedApp.when() calls.

        Example:
            @app.callback(
                Input('url', 'path'),
                Output('content-wrapper', 'content'),
            )
            def route_url(path: str) -> str:
                ...

        Args:
            dependencies: Positional arguments containing one or more observation Dependencies.
                May be original observation types (Modified/Select/Update) or aliased types (Input/State/Output).

        Returns:
            Decorator to register a function as an input/output reaction to one or more property changes.
        """
        return super().when(
            *dependencies,
        )


def Input(  # Treat this function as a class factory. pylint: disable=invalid-name
    id_or_exception: str | SupportsID | type[BaseException],
    property_or_event: str | type | None = None,
) -> InputType:
    """Initialize base dependency identification.

    Args:
        id_or_exception: ID, object with ID, or exception type, that a component uses to trigger callbacks.
        property_or_event: Property name, or event class type, on the component that triggers callbacks.

    Returns:
        Attribute watcher if provided strings, message watcher if string & class, or exception watcher if error type.

    Raises:
        ValueError if any combination of value is incorrect for conversion into an input type dependency
    """
    if isinstance(id_or_exception, str):
        if isinstance(property_or_event, str):
            return Modified(id_or_exception, property_or_event)
        if isinstance(property_or_event, type):
            return Published(id_or_exception, property_or_event)
        raise ValueError("Input dependency second argument can only be an attribute or class")
    if isinstance(id_or_exception, type) and issubclass(id_or_exception, BaseException):
        return Raised(id_or_exception)
    raise ValueError("Input dependency first argument can only be an id to watch or exception to catch")
