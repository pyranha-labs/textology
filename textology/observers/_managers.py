"""Managers for routing component input/output requests via observation callbacks."""

from __future__ import annotations

import abc
import asyncio
import functools
import logging
import traceback
from collections import defaultdict
from inspect import isawaitable
from typing import Any
from typing import Callable
from typing import Coroutine

from textology.logging import NullLogger

from ._dependencies import Dependency
from ._dependencies import Modified
from ._dependencies import NoUpdate
from ._dependencies import Select
from ._dependencies import Update
from ._dependencies import flatten_dependencies
from ._exceptions import PreventUpdate
from ._exceptions import UnknownObserver

# Type alias to represent function receiving 2 arguments (old value and new value) and returning nothing.
ValueUpdateHandler = Callable[[Any, Any], Coroutine]


class Observer:
    """Specification details for an input/output observer."""

    def __init__(
        self,
        modifications: list[Modified],
        selections: list[Select],
        updates: list[Update],
        callback: Callable | None = None,
        external: bool = False,
    ) -> None:
        """Initialize specifications for observing values.

        Args:
            modifications: Component IDs and properties that provide arguments and trigger the callback.
            selections: Component IDs and properties that provide additional arguments without triggering the callback.
            updates: Component IDs and properties to update based on the results of the callback.
            callback: The function to call with input values when triggered.
            external: Whether the callback is handled by an external endpoint, or locally.
                Any callbacks handled externally should be considered stateless: they should not store or request any
                variables created during previous callbacks, and should only rely on the arguments they provide.
                To share data across external callbacks, use an external storage type such as a database.
        """
        observer_id = (
            "..".join(f"{dep.component_id}@{dep.component_property}" for dep in modifications)
            + "..."
            + "..".join(f"{dep.component_id}@{dep.component_property}" for dep in updates)
        )
        self.observer_id = observer_id
        self.modifications = modifications
        self.selections = selections
        self.updates = updates
        self.callback = callback
        self.external = external

    def __hash__(self) -> int:
        """Convert object into hash usable in maps."""
        return hash(str(self))

    def __repr__(self) -> str:
        """Convert object into human-readable, machine loadable, text."""
        return (
            f"{self.__class__.__name__}("
            f"'{self.observer_id}',"
            f" {self.modifications},"
            f" {self.selections},"
            f" {self.updates},"
            f"external={self.external})"
        )


class ObserverManager:
    """Register and execute input/output callbacks when observed properties change.

    Can be used directly as a nested object within an application, or as a "mixin" for an application class. Example:
        manager = ObserverManager() # Or:
        class ObservedApp(ObserverManager):
            ...
        app = ObservedApp()
    """

    def __init__(
        self,
        logger: logging.Logger | None = None,
    ) -> None:
        """Initialize observation trackers and handlers.

        Args:
            logger: Custom logger to send messages to.
        """
        super().__init__()
        # Structured as: _observer_map[component_id][component_property] = Observer
        self._observer_map = defaultdict(lambda: defaultdict(list))
        self._observer_id_map = {}
        self.logger = logger or NullLogger(__name__)

    def apply_update(  # Pass all component arguments to allow subclasses to use. pylint: disable=unused-argument
        self,
        observer_id: str,
        component: Any,
        component_id: str,
        component_property: str,
        value: Any,
    ) -> None:
        """Apply a single update operation to a component.

        Default behavior is a standard attribute update. Override to provide more complex updates to properties.

        Args:
            observer_id: ID of the observer that requested the update.
            component: Component that the value update will be applied to.
            component_id: ID used to locate the updated component.
            component_property: Property name on the component that the updated value will be applied to.
            value: Updated value to apply to the property.
        """
        setattr(component, component_property, value)

    def _generate_callback(self, modified_id: str, modified_property: str, observer: Observer) -> ValueUpdateHandler:
        """Create a callback wrapper that will call the original function with input/output management applied."""

        async def _on_update(old_value: Any, new_value: Any) -> None:
            """Process value changes for a component property and apply the requested update operations."""
            update_components = self._get_update_components(observer)
            if not update_components:
                # One or more components missing, do not trigger callback.
                return
            observer_id = observer.observer_id
            args = []
            for dep in observer.modifications + observer.selections:
                if dep.component_id == modified_id and dep.component_property == modified_property:
                    args.append(old_value if isinstance(dep, Select) else new_value)
                else:
                    try:
                        args.append(
                            self.get_callback_arg(observer.observer_id, dep.component_id, dep.component_property)
                        )
                    except Exception as error:  # pylint: disable=broad-exception-caught
                        self.on_callback_error(observer_id, error)
                        return

            try:
                updates = observer.callback(*args) if not observer.external else self.send_callback(observer_id, *args)
                if isawaitable(updates):
                    updates = await updates
            except PreventUpdate:
                updates = None
            except BaseException as error:  # pylint: disable=broad-exception-caught
                # Catch all errors to prevent fatal crashes in application callback loops.
                self.on_callback_error(observer_id, error)
                updates = None

            if updates:
                try:
                    for update_id, properties in updates.items():
                        for update_property, value in properties.items():
                            self.apply_update(
                                observer_id, update_components[update_id], update_id, update_property, value
                            )
                except BaseException as error:  # pylint: disable=broad-exception-caught
                    # Catch all errors to prevent fatal crashes in application callback loops.
                    self.on_callback_error(observer_id, error)

        return _on_update

    def generate_callbacks(self, component_id: str, component_property: str) -> list[ValueUpdateHandler]:
        """Create callbacks that will manage input/output operations for all functions registered to id/property combo.

        Args:
            component_id: ID of a component with a property that will trigger callbacks.
            component_property: Property name on the component that will trigger callbacks.

        Returns:
            Callbacks to the original registered functions with automatic input/output management.
        """
        callbacks = []
        for observer in self._observer_map[component_id][component_property]:
            callbacks.append(self._generate_callback(component_id, component_property, observer))
        return callbacks

    def get_callback_arg(
        self,
        observer_id: str,
        component_id: str,
        component_property: str,
    ) -> Any:
        """Find a value from a component to be passed to a callback.

        Default behavior is a standard attribute request. Override to provide more complex request to properties.

        Args:
            observer_id: ID of the observer that triggered.
            component_id: ID of the component that contains the requested property.
            component_property: Property name on the component that is being requested.

        Returns:
            The property value from the requested component.
        """
        component = self.get_component(component_id)
        if not component:
            raise PreventUpdate(f"Skipping callback for {observer_id}: Component {component_id} not available")
        return getattr(component, component_property)

    @abc.abstractmethod
    def get_component(self, component_id: str) -> Any:
        """Fina a component for use in a callback.

        Args:
            component_id: ID of the component being requested.

        Returns:
            Component with properties usable in a callback.
        """

    def _get_update_components(self, observer: Observer) -> dict[str, Any] | None:
        """Find all components that will be updated by a callback."""
        output_components = {}
        for dep in observer.updates:
            component = self.get_component(dep.component_id)
            if not component:
                return None
            output_components[dep.component_id] = component
        return output_components

    def on_callback_error(self, observer_id: str, error: BaseException) -> None:
        """Action to perform when a callback fails.

        Args:
            observer_id: ID of the observer that failed to run the callback.
            error: Original error that caused the failure.

        Raises:
            Original error if lower level than Exception type.
        """
        if not isinstance(error, Exception):
            # Unhandled fatal error; reraise.
            raise error
        # Not all third party loggers have ".exception()" to print stacktraces, collect manually and use error.
        full_trace = traceback.format_exc()
        # Standard error, log and continue.
        self.logger.error(f"Failed callback for {observer_id}: {type(error).__name__} {error}\n{full_trace}")

    def send_callback(self, observer_id: str, *callback_args: Any) -> dict[str, dict[str, Any]]:
        """Forward a callback request to be handled externally.

        Override to send the request to an external endpoint, and wait for the response.
        Any callbacks handled externally should be considered stateless: they should not store or request any
        variables created during a previous callback, and should only rely on the callback arguments they provide.

        Args:
            observer_id: ID of the observer callback being requested to run externally.
            callback_args: Arguments passed to the external callback handler.

        Returns:
            Updates to be applied to components by ID and property name.
        """
        # Default behavior directly forwards to the callback receiver (local callback). Override to send externally.
        observer = self._observer_id_map.get(observer_id)
        if not observer:
            raise UnknownObserver(f"Callback {observer_id} was requested but could not be found.")
        self.logger.warning(
            f'External callback {observer_id} is forwarding to local callback: override "send_callback" in {type(self)} or remove "external" from callback'
        )
        return observer.callback(*callback_args)

    def when(
        self,
        *args: Dependency,
    ) -> Callable:
        """Register a callback that triggers when observed values change.

        Example:
            @app.when(
                Modified('url', 'path'),
                Update('content-wrapper', 'content'),
            )
            def route_url(path: str) -> str:
                ...

        Args:
            args: Positional arguments containing one or more observation Dependencies.

        Returns:
            Decorator to register a function as an input/output reaction to one or more property changes.
        """
        return create_observer_register(
            self._observer_map,
            self._observer_id_map,
            *args,
        )


class ObservedObject:
    """Basic object that triggers callbacks when observed values change.

    Example:
        class Observed(ObservedObject):
            value1 = ObservedValue('foo', lambda o, n: print(f'value1 updated from {o} > {n}'))
            value2 = ObservedValue('bar', lambda o, n: print(f'value2 updated from {o} > {n}'))
    """

    def __init__(self) -> None:
        """Initialize observed attributes."""
        self._observed_values: dict[str, ObservedValue] = {}
        self.__setup_observers__()

    def __getattribute__(self, name: str) -> Any:
        """Route attribute request to observed value container, or original attribute."""
        if name != "_observed_values" and name in self._observed_values:
            return self._observed_values[name].value
        return super().__getattribute__(name)

    def __setattr__(self, name: str, value: Any) -> None:
        """Route attribute update request to observed value container, or original attribute."""
        if name != "_observed_values" and name in self._observed_values:
            observer = self._observed_values[name]
            old_value = observer.value
            observer.value = value
            if old_value != value and observer.callback:
                result = observer.callback(old_value, value)
                if isawaitable(result):
                    loop = asyncio.get_event_loop()
                    loop.create_task(result)
        else:
            super().__setattr__(name, value)

    def __setup_observers__(self) -> None:
        """Initialize all observed attributes for updates."""
        for name in dir(self):
            value = getattr(self, name)
            if isinstance(value, ObservedValue):
                # Transpose the observed value container to an instance specific container to prevent class mutations.
                transposed = ObservedValue(value.value, value.callback)
                setattr(self, name, transposed)
                self._observed_values[name] = transposed

    def observe(self, name: str, callback: ValueUpdateHandler) -> None:
        """Update the callback on an observed value."""
        if name in self._observed_values:
            self._observed_values[name].callback = callback

    @property
    def observed_values(self) -> dict[str, ObservedValue]:
        """Provide all observed attribute containers."""
        return dict(self._observed_values)


class ObservedValue:
    """Basic container for a value that is monitored for changes by ObservedObject."""

    def __init__(self, value: Any, callback: ValueUpdateHandler | None = None) -> None:
        """Initialize the value and update function.

        Args:
            value: The initial value.
            callback: Where to send old and new values on update.
        """
        self.value = value
        self.callback = callback


def _create_callback(func: Callable, updates: list[Update]) -> Callable:
    """Wrap a function with additional callback management, such as error handling and result standardization."""

    @functools.wraps(func)
    async def _callback(*args: Any, **kwargs: Any) -> dict[str, dict[str, Any]]:
        """Wrap original function with additional callback management such as conversion to standardized result map."""
        results = func(*args, **kwargs)  # Invoke original callback.
        if isawaitable(results):
            results = await results
        if not isinstance(results, (list, tuple)):
            results = [results]

        if results is NoUpdate or isinstance(results, NoUpdate):
            raise PreventUpdate()

        component_updates = defaultdict(dict)
        has_update = False
        for update_val, update in zip(results, updates):
            if update_val is NoUpdate or isinstance(update_val, NoUpdate):
                continue
            has_update = True
            component_updates[update.component_id][update.component_property] = update_val

        if not has_update:
            raise PreventUpdate()

        return component_updates

    return _callback


def create_observer_register(
    observer_map: dict[str, dict[str, list[Observer]]],
    observer_id_map: dict[str, Observer],
    *observer_args: Any,
    split_modifications: bool = False,
    external: bool = False,
) -> Callable:
    """Create a decorator that will wrap a function with additional callback management, and register the observer.

    Args:
        observer_map: All currently registered observers by component ID and component property.
            Modified in place when new observer is registered.
        observer_id_map: All currently registered observers by full observer ID.
            Modified in place when new observer is registered.
        observer_args: Positional arguments containing one or more Dependencies.
        split_modifications: Register the observer once per Modification, instead of once per all Modifications.
        external: Whether the callback is handled by an external endpoint, or locally.
            Any callbacks handled externally should be considered stateless: they should not store or request any
            variables created during a previous callback, and should only rely on the callback arguments they provide.

    Returns:
        Decorator to register a function as an input/output reaction to one or more property changes.
    """

    def _decorator(func: Callable) -> Callable:
        """Wrap the original function with additional callback management, and register the final observer."""
        modifications, selections, updates = flatten_dependencies(observer_args)
        callback = _create_callback(func, updates)
        for modification_group in [[dep] for dep in modifications] if split_modifications else [modifications]:
            observer = Observer(
                modification_group,
                selections,
                updates,
                callback=callback,
                external=external,
            )
            observer_id_map[observer.observer_id] = observer
            for dep in modification_group:
                observer_map[dep.component_id][dep.component_property].append(observer)
        return callback

    return _decorator
