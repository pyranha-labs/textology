"""Managers for routing component input/output requests via observation callbacks."""

from __future__ import annotations

import abc
import asyncio
import itertools
import logging
import traceback
import weakref
from asyncio import iscoroutine
from collections import defaultdict
from functools import lru_cache
from typing import Any
from typing import Callable
from typing import Coroutine
from typing import Generator

from textology.logging import NullLogger

from ._dependencies import Dependency
from ._dependencies import DependencyType
from ._dependencies import Modified
from ._dependencies import NoUpdate
from ._dependencies import Published
from ._dependencies import Raised
from ._dependencies import Select
from ._dependencies import Update
from ._dependencies import flatten_dependencies
from ._dependencies import no_update
from ._dependencies import validate_dependencies
from ._exceptions import PreventUpdate
from ._exceptions import UnknownObserver

UpdateResultType = dict[str, dict[str, Any]]

# Type alias to represent function receiving 2 arguments (old value and new value) and returning nothing.
ValueUpdateHandler = Callable[[Any, Any], Coroutine]

_GLOBAL_OBSERVER_EXC_MAP: dict[type[Exception], list[Observer]] = defaultdict(list)
_GLOBAL_OBSERVER_ID_MAP: dict[str, Observer] = {}
_GLOBAL_OBSERVER_MAP: dict[str, dict[str, list[Observer]]] = defaultdict(lambda: defaultdict(list))

CALLBACK_CACHE_SIZE = 1024
WHEN_DECORATOR = "_textology_when"


class Observer:
    """Specification details for an input/output observer.

    External callbacks should be considered stateless: they should not store or request any
    variables created during previous callbacks, and should only rely on the arguments they provide.
    To share data across external callbacks, use an external storage type such as a database.
    """

    def __init__(
        self,
        dependencies: dict[type[Dependency], list[Dependency]],
        func: Callable = False,
        external: bool = False,
    ) -> None:
        """Initialize specifications for observing values.

        Args:
            dependencies: Dependencies used to monitor for triggers and results of the callback.
            func: The function to call with input values when triggered.
                Indirectly called via "callback()" when triggered.
            external: Whether the callback is handled locally, or sent to an external handler.
        """
        self._dependencies: dict[type[Dependency], list[DependencyType]] = dependencies or {}
        for dependency_type in (Modified, Published, Raised, Select, Update):
            self._dependencies.setdefault(dependency_type, [])
        self._method_ref: weakref.ReferenceType | None = None
        self.external = external
        self.func = func
        self._callback_arguments = self.publications + self.modifications + self.selections
        inputs = self.publications + self.modifications + self.raises + self.selections
        outputs = self.updates
        self.id = (
            "+".join(f"{dep.component_id}@{dep.component_property}" for dep in inputs)
            + "->"
            + "+".join(f"{dep.component_id}@{dep.component_property}" for dep in outputs)
        )

        # If the function is not a method (object pre-attached), then tag it in case an object needs to be added.
        # Tagged functions can be searched later, such as during object init, to convert the callback into a method.
        if type(func).__name__ != "method":
            if not hasattr(func, WHEN_DECORATOR):
                setattr(func, WHEN_DECORATOR, [])
            getattr(func, WHEN_DECORATOR).append(self)

    def __hash__(self) -> int:
        """Convert object into hash usable in maps."""
        return hash(str(self))

    def __repr__(self) -> str:
        """Convert object into human-readable, machine loadable, text."""
        return f"{self.__class__.__name__}({self._dependencies})"

    async def callback(self, *args: Any, **kwargs: Any) -> UpdateResultType | None:
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
        results = await results if iscoroutine(results) else results

        if isinstance(results, NoUpdate) or not self.updates:
            return None

        if len(self.updates) == 1:
            results = [results]

        component_updates = defaultdict(dict)
        has_update = False
        for update_val, update in zip(results, self.updates):
            if isinstance(update_val, NoUpdate):
                continue
            has_update = True
            component_updates[update.component_id][update.component_property] = update_val

        if not has_update:
            return None

        return component_updates

    @property
    def callback_arguments(self) -> list[Published | Modified | Select]:
        """Component IDs and properties, or types, that provide arguments to the callback."""
        return self._callback_arguments

    @property
    def modifications(self) -> list[Modified]:
        """Component IDs and properties that provide arguments and trigger the callback."""
        return self._dependencies[Modified]

    @property
    def publications(self) -> list[Published]:
        """Component IDs and published event types that provide arguments and trigger the callback."""
        return self._dependencies[Published]

    @property
    def raises(self) -> list[Raised]:
        """Exception types that provide arguments and trigger the callback when an exception is raised."""
        return self._dependencies[Raised]

    @property
    def selections(self) -> list[Select]:
        """Component IDs and properties that provide additional arguments without triggering the callback."""
        return self._dependencies[Select]

    def update_method_ref(self, obj: Any) -> None:
        """Update the weak reference used when the callback is a method.

        Args:
            obj: Object to store a new weak reference for, and use during callbacks.
        """
        self._method_ref = weakref.ref(obj)

    @property
    def updates(self) -> list[Update]:
        """Component IDs and properties for output of a callback that will be updated after triggering."""
        return self._dependencies[Update]


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
        self._observer_exc_map: dict[type[Exception], list[Observer]] = defaultdict(list)
        self._observer_id_map: dict[str, Observer] = {}
        # Structured as: _observer_map[component_id][component_property] = Observers
        self._observer_map: dict[str, dict[str, list[Observer]]] = defaultdict(lambda: defaultdict(list))
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

    def _generate_callback(self, trigger_id: str, trigger_property: str, observer: Observer) -> ValueUpdateHandler:
        """Create a callback wrapper that will call the original function with input/output management applied."""

        async def _on_update(old_value: Any, new_value: Any) -> None:
            """Process value changes for a component property and apply the requested update operations."""
            update_components = self._get_update_components(observer)
            if observer.updates and not update_components:
                # One or more components are not in the current component tree, do not trigger callback.
                return
            callback_components = self._get_callback_components(observer)
            if not callback_components:
                # One or more components are not in the current component tree, do not trigger callback.
                return
            args = self._get_callback_args(
                observer,
                callback_components,
                trigger_id,
                trigger_property,
                old_value,
                new_value,
            )
            if isinstance(args, NoUpdate):
                # Failed to request one or more component properties, do not continue.
                return

            try:
                updates = observer.callback(*args) if not observer.external else self.send_callback(observer.id, *args)
                updates = await updates if iscoroutine(updates) else updates
            except PreventUpdate:
                updates = None
            except BaseException as error:  # pylint: disable=broad-exception-caught
                # Catch all errors to prevent fatal crashes in application callback loops.
                # All error updates will be handled separately, as the components will not be the same.
                updates = None
                if not await self._on_update_error(error):
                    # Send error to the default handler, nothing else was set up to capture.
                    self.on_callback_error(observer.id, error)

            if not updates:
                # There are no update types, updates were requested to be skipped, or generating updates failed.
                return

            try:
                for comp_id, comp_property, value in _iter_updates(updates):
                    self.apply_update(observer.id, update_components[comp_id], comp_id, comp_property, value)
            except BaseException as error:  # pylint: disable=broad-exception-caught
                # Catch all errors to prevent fatal crashes in application callback loops.
                self.on_callback_error(observer.id, error)

        return _on_update

    @lru_cache(maxsize=CALLBACK_CACHE_SIZE)
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
        component: Any,
        property_name: str,
    ) -> Any:
        """Find a value from a component to be passed to a callback.

        Default behavior is a standard attribute request. Override to provide more complex request to properties.

        Args:
            component: Component with properties usable in a callback.
            property_name: Name of the property on the component that is being requested.

        Returns:
            The property value from the requested component.
        """
        return getattr(component, property_name)

    def _get_callback_args(  # pylint: disable=too-many-arguments
        self,
        observer: Observer,
        components: dict,
        trigger_id: str | None,
        trigger_property: str | None,
        old_value: Any,
        new_value: Any,
    ) -> list | NoUpdate:
        """Find all arguments from components that will be used by a callback."""
        args = []
        for dep in observer.callback_arguments:
            if isinstance(dep, Published):
                # Published events are stateless; they are not available if they are not the trigger.
                # Fill events, other than the triggering event, with empty values.
                args.append(new_value if dep.component_id == trigger_id else None)
            elif dep.component_id == trigger_id and dep.component_property == trigger_property:
                # Properties are stateful; they are available at all times.
                # Use new value if this was the trigger, otherwise use historical value to represent "current" state.
                args.append(old_value if isinstance(dep, Select) else new_value)
            else:
                try:
                    args.append(self.get_callback_arg(components[dep.component_id], dep.component_property))
                except Exception as error:  # pylint: disable=broad-exception-caught
                    self.on_callback_error(observer.id, error)
                    return no_update
        return args

    def _get_callback_components(self, observer: Observer) -> dict[str, Any] | None:
        """Find all components that will be used as arguments by a callback."""
        output_components = {}
        for dep in observer.callback_arguments:
            component = self.get_component(dep.component_id)
            if not component:
                return None
            output_components[dep.component_id] = component
        return output_components

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
        components = {}
        for dep in observer.updates:
            component = self.get_component(dep.component_id)
            if not component:
                return None
            components[dep.component_id] = component
        return components

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

    async def _on_update_error(self, error: BaseException) -> bool:
        """Handle callback exception raises and apply the requested update operations."""
        handlers = None
        handled = False
        for exc_type in error.__class__.__mro__[:-1]:
            # Stop on the first match for the class, this will be the best match (most specific) for the type.
            if handlers := self._observer_exc_map.get(exc_type):
                break

        if not handlers:
            return handled

        for observer in handlers:
            update_components = self._get_update_components(observer)
            if observer.updates and not update_components:
                # One or more components are not in the current component tree, do not trigger callback.
                continue
            callback_components = self._get_callback_components(observer)
            if observer.callback_arguments and not callback_components:
                # One or more components are not in the current component tree, do not trigger callback.
                continue
            args = self._get_callback_args(
                observer,
                callback_components,
                None,
                None,
                None,
                None,
            )
            if isinstance(args, NoUpdate):
                # Failed to request one or more component properties, do not continue.
                continue

            try:
                updates = (
                    observer.callback(error, *args)
                    if not observer.external
                    else self.send_callback(
                        observer.id,
                        error,
                        *args,
                    )
                )
                updates = await updates if iscoroutine(updates) else updates

                if not updates:
                    if not update_components:
                        # No updates were expected, consider the exception handled by the callback.
                        handled = True
                    continue

                for comp_id, comp_property, value in _iter_updates(updates):
                    self.apply_update(observer.id, update_components[comp_id], comp_id, comp_property, value)
                    handled = True
            except PreventUpdate:
                pass
            except BaseException as new_error:  # pylint: disable=broad-exception-caught
                # Catch all errors to prevent fatal crashes in application callback loops.
                self.on_callback_error(observer.id, new_error)
        return handled

    async def send_callback(self, observer_id: str, *callback_args: Any) -> dict[str, dict[str, Any]]:
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
        return await observer.callback(*callback_args)

    def when(
        self,
        *dependencies: Dependency,
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
            dependencies: Positional arguments containing one or more observation Dependencies.

        Returns:
            Decorator to register a function as an input/output reaction to one or more property changes.
        """
        return create_observer_register(
            *dependencies,
            observer_exc_map=self._observer_exc_map,
            observer_id_map=self._observer_id_map,
            observer_map=self._observer_map,
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
                if iscoroutine(result):
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
    *dependencies: Dependency,
    observer_exc_map: dict[type[Exception], list[Observer]] | None = None,
    observer_id_map: dict[str, Observer] | None = None,
    observer_map: dict[str, dict[str, list[Observer]]] | None = None,
    split_publications: bool = True,
    split_modifications: bool = False,
    split_raises: bool = True,
    external: bool = False,
) -> Callable:
    """Create a decorator that will wrap a function with additional callback management, and register the observer.

    Args:
        dependencies: Positional arguments containing one or more Dependencies.
        observer_exc_map: All currently registered observers for Exception types.
            Modified in place when observer is registered. Defaults to global exception observers shared across apps.
        observer_id_map: All currently registered observers by full observer ID.
            Modified in place when observer is registered. Defaults to global observers shared across apps.
        observer_map: All currently registered observers by component ID and component property.
            Modified in place when observer is registered. Defaults to global observers shared across apps.
        split_publications: Register the observer once per publication, instead of once per all publications.
        split_modifications: Register the observer once per modification, instead of once per all modifications.
        split_raises: Register the observer once per exception raise type, instead of once per all raise types.
        external: Whether the callback is handled by an external endpoint, or locally.
            Any callbacks handled externally should be considered stateless: they should not store or request any
            variables created during a previous callback, and should only rely on the callback arguments they provide.

    Returns:
        Decorator to register a function as an input/output reaction to one or more property changes.
    """
    validate_dependencies(*dependencies)

    observer_exc_map = observer_exc_map if observer_exc_map is not None else _GLOBAL_OBSERVER_EXC_MAP
    observer_id_map = observer_id_map if observer_id_map is not None else _GLOBAL_OBSERVER_ID_MAP
    observer_map = observer_map if observer_map is not None else _GLOBAL_OBSERVER_MAP

    def _decorator(func: Callable) -> Callable:
        """Wrap the original function with additional callback management, and register the final observer."""
        observers = []
        flattened = flatten_dependencies(dependencies)
        publications = flattened.get(Published, [])
        modifications = flattened.get(Modified, [])
        raises = flattened.get(Raised, [])
        selections = flattened.get(Select, [])
        updates = flattened.get(Update, [])

        # Create all standard observers, those that are not based on exceptions will all combinations.
        # Triggers can be 1 input/argument per callback, or all per callback.
        if publications:
            publications = [[dep] for dep in publications] if split_publications else [publications]
        if modifications:
            modifications = [[dep] for dep in modifications] if split_modifications else [modifications]
        for publication_group, modification_group in itertools.product(publications or [[]], modifications or [[]]):
            observers.append(
                Observer(
                    {
                        Published: publication_group,
                        Modified: modification_group,
                        Select: selections,
                        Update: updates,
                    },
                    func=func,
                    external=external,
                )
            )

        # Create all special exception observers with only raise types, selections, and updates.
        if raises:
            raises = [[dep] for dep in raises] if split_raises else [raises]
        for raise_group in raises:
            observers.append(
                Observer(
                    {
                        Raised: raise_group,
                        Select: selections,
                        Update: updates,
                    },
                    func=func,
                    external=external,
                )
            )

        for observer in observers:
            observer_id_map[observer.id] = observer
            for dep in observer.publications + observer.modifications:
                observer_map.setdefault(dep.component_id, {}).setdefault(dep.component_property, []).append(observer)
            for dep in observer.raises:
                observer_exc_map.setdefault(dep.exception_type, []).append(observer)

        # Return the original, unmodified, function; the decorator only tags and/or maps for later usage.
        return func

    return _decorator


def _iter_updates(updates: UpdateResultType) -> Generator[tuple[str, str, Any], None, None]:
    """Iterate over the standard update multi-level format."""
    for update_id, properties in updates.items():
        for update_property, value in properties.items():
            yield update_id, update_property, value


def when(
    *dependencies: Dependency,
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
        dependencies: Positional arguments containing one or more observation Dependencies.

    Returns:
        Decorator to register a function as an input/output reaction to one or more property changes.
    """
    return create_observer_register(
        *dependencies,
    )
