
# Roadmap

Planned features and functionality. Not an all-inclusive list.


## Features

Core features and functionality.

- [x] Observers
    * [x] General manager for registering input/output callbacks based on observing values
    * [x] ObserverApp utilizing observer manager for automating reactive attribute events
    * [ ] Observer dependency filters (greater than, less than, equals, where, etc.)
    * [ ] Wildcard/variable observers similar to routes (all, match)
    * [ ] Background callbacks
      * [ ] "running" callbacks to show immediate change before completion
      * [ ] "progress" callbacks to update the status of "running" callbacks
      * [ ] "cancel" callbacks to stop "running" callbacks
- [x] Routers
    * [x] Basic URL router with variables in paths
    * [x] Endpoint methods for leverage same routes with different operations
- [ ] HTML templates for layouts
- [x] Testing
    * [x] Parallel processing support (python-xdist)
    * [x] Async support (python-asyncio)
    * [x] MDL HTML report for failed snapshot tests
    * [ ] Update MDL to MDC for HTML report


## Widgets

New widgets to expand the available base use cases.

- [x] HorizontalMenus (progressive horizontal set of ListViews with peeking)
- [x] Location (URL type storage for simple routing of "paged" applications)
- [x] Store (arbitrary data storage for sharing values between callbacks)
- [x] ModalDialog (dialog to accept arbitrary widgets without new class)
- [ ] Interval (periodic callbacks)


## Widget Extensions

Functionality to expand the use cases of existing widgets.

- [x] Base widget extensions
    * [x] Support per-instance message disables
    * [x] Support per-instance "on_*" message callbacks
    * [x] Support per-instance styles
    * [x] Button with reactive "clicks" attributes
    * [x] ListItem with metadata objects
    * [x] ListItemHeader (ListItem subclass) for non-interactive section breaks in ListViews
    * [x] ListView with reactive "highlighted" attributes, and support for ListItemHeaders
    * [ ] Extend Remainder of "containers" module
    * [ ] Extend Remainder of "widgets" module
