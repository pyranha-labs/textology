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

from textology.apps import ExtendedApp

# Compatibility aliases for Dash.
from textology.observers import Dependency
from textology.observers import Modified
from textology.observers import NoUpdate  # pylint: disable=unused-import
from textology.observers import Published
from textology.observers import Select as State  # pylint: disable=unused-import
from textology.observers import SupportsID
from textology.observers import Update as Output  # pylint: disable=unused-import
from textology.observers import when as callback  # pylint: disable=unused-import

InputType = Modified | Published


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
    component_id: str | SupportsID,
    property_or_event: str | type,
) -> InputType:
    """Initialize base dependency identification.

    Args:
        component_id: ID, or object with ID property, that a component uses to send and receive updates.
        property_or_event: Property name, or event class type, on the component that triggers callbacks.

    Return:
        Reactive attribute dependency (Modified) if a string, message dependency (Published) otherwise.
    """
    if not isinstance(str, type):
        raise ValueError("Input dependencies can only be strings, or classes")
    if isinstance(property_or_event, str):
        return Modified(component_id, property_or_event)
    return Published(component_id, property_or_event)
