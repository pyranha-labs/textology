"""Managers for routing component input/output requests via observation callbacks."""

from __future__ import annotations

import abc
import asyncio
import itertools
import logging
import traceback
import weakref
from collections import defaultdict
from inspect import isawaitable
from typing import Any
from typing import Callable
from typing import Coroutine

from textology.logging import NullLogger

from ._dependencies import Dependency
from ._dependencies import Modified
from ._dependencies import NoUpdate
from ._dependencies import Published
from ._dependencies import Select
from ._dependencies import Update
from ._dependencies import flatten_dependencies
from ._exceptions import PreventUpdate
from ._exceptions import UnknownObserver

# Type alias to represent function receiving 2 arguments (old value and new value) and returning nothing.
ValueUpdateHandler = Callable[[Any, Any], Coroutine]

_GLOBAL_OBSERVER_ID_MAP: dict[str, Observer] = {}
_GLOBAL_OBSERVER_MAP: dict[str, dict[str, list[Observer]]] = defaultdict(lambda: defaultdict(list))

WHEN_DECORATOR = "_textology_when"


class Observer:
    """Specification details for an input/output observer.

    External callbacks should be considered stateless: they should not store or request any
    variables created during previous callbacks, and should only rely on the arguments they provide.
    To share data across external callbacks, use an external storage type such as a database.
    """

    def __init__(
        self,
        publications: list[Published],
        modifications: list[Modified],
        selections: list[Select],
        updates: list[Update],
        func: Callable = False,
    ) -> None:
        """Initialize specifications for observing values.

        Args:
            publications: Component IDs and published event types that provide arguments and trigger the callback.
            modifications: Component IDs and properties that provide arguments and trigger the callback.
            selections: Component IDs and properties that provide additional arguments without triggering the callback.
            updates: Component IDs and properties to update based on the results of the callback.
            func: The function to call with input values when triggered.
                Indirectly called via "callback()" when triggered.
        """
        observer_id = (
            "..".join(f"{dep.component_id}@{dep.component_property}" for dep in publications + modifications)
            + "..."
            + "..".join(f"{dep.component_id}@{dep.component_property}" for dep in updates)
        )
        self._method_ref: weakref.ReferenceType | None = None
        self.observer_id = observer_id
        self.publications = publications
        self.modifications = modifications
        self.selections = selections
        self.updates = updates
        self.external = False
        self.func = func

    def __hash__(self) -> int:
        """Convert object into hash usable in maps."""
        return hash(str(self))

    def __repr__(self) -> str:
        """Convert object into human-readable, machine loadable, text."""
        return (
            f"{self.__class__.__name__}("
            f"'{self.publications}',"
            f" {self.modifications},"
            f" {self.selections},"
            f" {self.updates},"
            f"external={self.external})"
        )

    async def callback(self, *args: Any, **kwargs: Any) -> dict[str, dict[str, Any]] | None:
        """Call the original function with additional callback management, such as conversion to standardized results.

        Args:
            args: Original positional arguments for function.
            kwargs: Original keyword arguments for function.

        Returns:
            A mapping of all results by component ID and property.
        """
        func = self.func
        if self._method_ref:
            ref = self._method_ref()
            if ref:
                func = func.__get__(ref)  # Required to access the method. pylint: disable=unnecessary-dunder-call
        results = func(*args, **kwargs)  # Invoke original callback.
        results = await results if isawaitable(results) else results

        if results is NoUpdate or isinstance(results, NoUpdate) or not self.updates:
            return None

        if len(self.updates) == 1:
            results = [results]

        component_updates = defaultdict(dict)
        has_update = False
        for update_val, update in zip(results, self.updates):
            if update_val is NoUpdate or isinstance(update_val, NoUpdate):
                continue
            has_update = True
            component_updates[update.component_id][update.component_property] = update_val

        if not has_update:
            return None

        return component_updates

    def update_method_ref(self, obj: Any) -> None:
        """Update the weak reference used when the callback is a method.

        Args:
            obj: Object to store a new weak reference for, and use during callbacks.
        """
        self._method_ref = weakref.ref(obj)


class ObserverManager:
    """Register and execute input/output callbacks when observed properties change.

    Can be used directly as a nested object within an application, or as a "mixin" for an application class. Example:
        manager = ObserverManager() # Or:
        class ObservedApp(BaseAppClass, ObserverManager):
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
        self._observer_id_map = {}
        # Structured as: _observer_map[component_id][component_property] = Observer
        self._observer_map = defaultdict(lambda: defaultdict(list))
        self.logger: logging.Logger | None = logger or NullLogger(__name__)

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

    @staticmethod
    def attach_to_observers(obj: Any) -> None:
        """Allow observers to call functions as methods with required references if registered at the class level.

        Args:
            obj: Fully instantiated object with or without functions decorated as observers.
        """
        for value in obj.__class__.__dict__.values():
            if callable(value):
                observers = getattr(value, WHEN_DECORATOR, None)
                if observers:
                    for observer in observers:
                        observer.update_method_ref(obj)

    def _generate_callback(self, trigger_id: str, modified_property: str, observer: Observer) -> ValueUpdateHandler:
        """Create a callback wrapper that will call the original function with input/output management applied."""

        async def _on_update(old_value: Any, new_value: Any) -> None:
            """Process value changes for a component property and apply the requested update operations."""
            update_components = self._get_update_components(observer)
            if observer.updates and not update_components:
                # One or more components missing, do not trigger callback.
                return
            observer_id = observer.observer_id
            args = []
            for dep in observer.publications + observer.modifications + observer.selections:
                if isinstance(dep, Published):
                    # Published events are stateless; they are not available if they are not the trigger.
                    # Fill events, other than the triggering event, with empty values.
                    args.append(new_value if dep.component_id == trigger_id else None)
                elif dep.component_id == trigger_id and dep.component_property == modified_property:
                    # Properties are stateful; they are available at all times.
                    # Use new value if this was the trigger, otherwise use historical value to represent "current" state.
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
                updates = await updates if isawaitable(updates) else updates
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
        for observer in self._observer_map_global[component_id][component_property]:
            callbacks.append(self._generate_callback(component_id, component_property, observer))
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

    @property
    def _observer_id_map_global(self) -> dict[str, Observer]:
        """Return the global observer ID map used across all managers.

        The global observer ID map is populated when functions are decorated at the class or module level.
        """
        return _GLOBAL_OBSERVER_ID_MAP

    @property
    def _observer_map_global(self) -> dict[str, dict[str, list[Observer]]]:
        """Return the global observer map used across all managers.

        The global observer map is populated when functions are decorated at the class or module level.
        """
        return _GLOBAL_OBSERVER_MAP

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
        """Register a callback that triggers when observed values change while this instance is active.

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


def create_observer_register(
    observer_map: dict[str, dict[str, list[Observer]]],
    observer_id_map: dict[str, Observer],
    *observer_args: Dependency,
    split_publications: bool = False,
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
        split_publications: Register the observer once per publication, instead of once per all publications.
        split_modifications: Register the observer once per modification, instead of once per all modifications.
        external: Whether the callback is handled by an external endpoint, or locally.
            Any callbacks handled externally should be considered stateless: they should not store or request any
            variables created during a previous callback, and should only rely on the callback arguments they provide.

    Returns:
        Decorator to register a function as an input/output reaction to one or more property changes.
    """

    def _decorator(func: Callable) -> Callable:
        """Wrap the original function with additional callback management, and register the final observer."""
        publications, modifications, selections, updates = flatten_dependencies(observer_args)

        # Triggers can be 1 input/argument per callback, or all per callback.
        if publications:
            publications = [[dep] for dep in publications] if split_publications else [publications]
        if modifications:
            modifications = [[dep] for dep in modifications] if split_modifications else [modifications]

        observers = []
        for publication_group, modification_group in itertools.product(publications or [[]], modifications or [[]]):
            observers.append(
                Observer(
                    publication_group,
                    modification_group,
                    selections,
                    updates,
                    func=func,
                )
            )
        for observer in observers:
            observer.external = external
            # If the function is not a method (object pre-attached), then tag it in case an object needs to be added.
            # Tagged functions can be searched later, such as during object init, to convert the callback into a method.
            if type(func).__name__ != "method":
                if not hasattr(func, WHEN_DECORATOR):
                    setattr(func, WHEN_DECORATOR, [])
                getattr(func, WHEN_DECORATOR).append(observer)
            observer_id_map[observer.observer_id] = observer
            for dep in observer.publications + observer.modifications:
                observer_map.setdefault(dep.component_id, {}).setdefault(dep.component_property, []).append(observer)

        # Return the original, unmodified, function; the decorator only tags and/or maps for later usage.
        return func

    return _decorator


def when(
    *args: Dependency,
) -> Callable:
    """Register a callback that triggers when observed values change globally.

    Example:
        @when(
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
        _GLOBAL_OBSERVER_MAP,
        _GLOBAL_OBSERVER_ID_MAP,
        *args,
    )
