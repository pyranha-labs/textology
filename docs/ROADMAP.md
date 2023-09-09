
# Roadmap

Planned features and functionality. Not an all-inclusive list.


## Features

Core features and functionality.

- [x] Observers
    * [x] General manager for registering input/output callbacks based on observing value changes
      * [x] Register input/output callbacks based on observing stateful attributes
      * [x] Register input/output callbacks based on observing stateless events
      * [x] Register input/output callbacks based on observing exceptions
    * [x] ExtendedApp utilizing observer manager for automating reactions to application changes
      * [x] Support for input/output callbacks based on reactive attribute updates
      * [x] Support for input/output callbacks based on monitoring stateless message events
      * [x] Support for input/output callbacks based on monitoring exceptions
    * [x] ExtendedApp compatibility layer with Dash syntax (allow Dash style callback declarations)
    * [x] Register global input/output callbacks used across all observer managed applications
      * [x] Register callbacks against module level functions
      * [x] Register callbacks against instance methods
      * [ ] Register callbacks against class methods
      * [ ] Register callbacks against static methods
    * [ ] Observer dependency filters (greater than, less than, equals, where, etc.)
    * [ ] Wildcard/variable observers similar to routes (all, match)
    * [ ] Background callbacks
      * [ ] "running" callbacks to show immediate change before completion
      * [ ] "progress" callbacks to update the status of "running" callbacks
      * [ ] "cancel" callbacks to stop "running" callbacks
    * [ ] Allowing controlling whether callbacks are triggered on first load with "prevent_initial_call"
- [x] Routers
    * [x] Basic URL router with variables in paths
    * [x] Endpoint methods for leverage same routes with different operations
    * [x] ExtendedApp with multi-page widget routing via URLs
      * [x] Register pages via direct layout function
      * [x] Register pages via modules with layout functions
      * [ ] Register pages via class tree to allow flexible module layout
      * [ ] Allow registering all modules in a folder
      * [ ] Allow full folder path to page path. e.g. "docs/doc1" to "/docs/doc1"
      * [ ] Allow full module name to page path. e.g. "docs.doc1" to "/docs/doc1"
    * [ ] Async router serve loop
- [x] Custom themes
    * [x] Named themes by CSS paths
    * [ ] Named themes by raw CSS
    * [ ] Multiple simultaneous themes
- [ ] HTML templates for layouts
- [x] Testing
    * [x] Parallel processing support (python-xdist)
    * [x] Async support (python-asyncio)
    * [x] MDL HTML report for failed snapshot tests
    * [x] Update MDL to MDC for HTML report
    * [ ] Add JSON view of widget tree to test failure output


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
    * [x] Extend Remainder of "containers" module
    * [x] Extend Remainder of "widgets" module
