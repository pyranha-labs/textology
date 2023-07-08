"""Dash compatibility layer for creating Textual applications in "Plotly Dash" code style.

The goal of this library is to provide a familiar interface for developers who have worked with Plotly Dash
to make UI web applications, due to usage of similar principles. This can be used for basic applications,
and to help transition developers to the style used in Textology for "observation pattern" type applications.

While this library provides compatibility across frameworks in style where possible, it is not a guarantee or promise
for any specific features or functionality. If a feature in Textology extended applications has an equivalent in Dash,
it will be included here, but this is not Dash. In order to access the full range of Textology and Textual features,
developers should leverage the native classes and designs from the standard library.
"""

from typing import Callable

from textology.apps import ObservedApp

# Compatibility aliases for Dash.
from textology.observers import Dependency
from textology.observers import Modified as Input  # pylint: disable=unused-import
from textology.observers import Select as State  # pylint: disable=unused-import
from textology.observers import Update as Output  # pylint: disable=unused-import


class DashCompatApp(ObservedApp):
    """Application capable of performing automatic input/output callbacks on reactive widget property updates.

    Compatibility alias for ObservedApp class.
    """

    def callback(
        self,
        *args: Dependency,
    ) -> Callable:
        """Register a callback that triggers when observed values change.

        Compatibility alias for ObservedApp.when() calls.

        Example:
            @app.callback(
                Input('url', 'path'),
                Output('content-wrapper', 'content'),
            )
            def route_url(path: str) -> str:
                ...

        Args:
            args: Positional arguments containing one or more observation Dependencies.
                May be original observation types (Modified/Select/Update) or aliased types (Input/State/Output).

        Returns:
            Decorator to register a function as an input/output reaction to one or more property changes.
        """
        return super().when(
            self._observer_map,
            self._observer_id_map,
            *args,
        )
