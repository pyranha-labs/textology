
<div align="center">
  <img src="https://raw.githubusercontent.com/pyranha-labs/textology/main/docs/banner.svg" width="450">
</div>

-----------------


[![os: windows mac linux](https://img.shields.io/badge/os-linux_|_macos_|_windows-blue)](https://docs.python.org/3.10/)
[![python: 3.10+](https://img.shields.io/badge/python-3.10_|_3.11-blue)](https://devguide.python.org/versions)
[![python style: google](https://img.shields.io/badge/python%20style-google-blue)](https://google.github.io/styleguide/pyguide.html)
[![imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://github.com/PyCQA/isort)
[![code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![code style: pycodestyle](https://img.shields.io/badge/code%20style-pycodestyle-green)](https://github.com/PyCQA/pycodestyle)
[![doc style: pydocstyle](https://img.shields.io/badge/doc%20style-pydocstyle-green)](https://github.com/PyCQA/pydocstyle)
[![static typing: mypy](https://img.shields.io/badge/static_typing-mypy-green)](https://github.com/python/mypy)
[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/PyCQA/pylint)
[![testing: pytest](https://img.shields.io/badge/testing-pytest-yellowgreen)](https://github.com/pytest-dev/pytest)
[![security: bandit](https://img.shields.io/badge/security-bandit-black)](https://github.com/PyCQA/bandit)
[![license: MIT](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)


# Textology

### The study of making interactive UIs with text.

Why should GUIs have all the fun? Textology extends the amazing functionality of
[Textual](https://github.com/Textualize/textual) and [Rich](https://github.com/Textualize/rich),
to help create TUIs with popular UI design patterns and principals from web and mobile frameworks.
Refer to [Top Features](#top-features) for a summary of the extensions provided.

#### Additional Background

Commonly known as Text (or Terminal) User Interfaces, the goal of a TUI (Tooey) is to provide as close
as possible to a traditional GUI experience straight from a terminal. Why? Not all environments allow full graphical
library access, web access, etc., but almost all provide access from a terminal. Yes, even terminals can provide
mouse support, sophisticated layouts, animations, and a wide range of colors!

Like Textual, Textology is inspired by modern web development. Textology extends Textual by bringing together, and
expanding upon, designs from other frameworks such as Dash/FastAPI/Flask, including their use of routing, annotations,
and observation patterns. Why? To increase developer velocity based on existing experience. Textology also receives
inspiration from other UI frameworks external to Python, such as iOS, Android, and Web frameworks. Most importantly
however, Textology is an extension of Textual: it does not replace Textual, but rather provides additional options
on top of the core Textual framework.

Before using Textology, be comfortable with Textual. For tutorials, guides, etc., refer to the
[Textual Documentation](https://textual.textualize.io/guide/). Textology is NOT a replacement for Textual, it is an
extension. Callbacks, widgets, screens, event lifecycles, etc., from Textual still apply to Textology extended
widgets and applications. For other advanced features, familiarity with Dash/FastAPI/Flask principles will help.
Examples for Textology extensions, such as callback based applications, are included in this documentation.


## Table Of Contents

  * [Top Features](#top-features)
  * [Compatibility](#compatibility)
  * [Getting Started](#getting-started)
    * [Installation](#installation)
    * [Extended Applications](#extended-applications)
    * [Extended Widgets](#extended-widgets)
    * [Extended Testing](#extended-testing)


## Top Features

- Multiple theme support
  - Swap CSS themes live
  - Apply multiple CSS themes simultaneously
- Extended callbacks
  - Declare Widget callbacks/event handling on instantiation or subclassing
  - Add Widget callbacks after instantiation
  - Use temporary callbacks that only trigger once
  - Declare Apps with "event driven architecture/observation pattern" to detect changes and automatically update UI
    - Listen to reactive attribute changes.
    - Listen to events/messages/errors.
- Extended native widgets, including (but not limited to):
  - All widgets: ability to disable event messages and declare styles without subclassing
  - ListItems with data objects
  - Buttons with automatic tracking of click counts
- New widgets, including (but not limited to):
  - ListItemHeaders (non-interactive ListItems)
  - HorizontalMenus (walkable list of ListViews with peeking at following lists)
  - MultiSelect (dropdown list with ability to select multiple items).
- Enhanced testing support
  - Parallel tests via python-xdist
  - Custom testing arguments, such as updating snapshots on failures


## Compatibility

Textology follows [Textual Compatibility](https://github.com/Textualize/textual#compatibility) guidelines with one
exception: Python3.10 minimum requirement.


## Getting Started

### Installation

Install Textology via pip:
```shell
pip install textology
```

For development of applications based on Textual/Textology (but not development of Textology itself), use the
`[dev]` package. This installs extra Textual development tools, and requirements for Textology testing extensions.
```shell
pip install textology[dev]
```

For full development of Textology itself, refer to [Contributing](CONTRIBUTING.md). This installs Textual development tools,
requirements for Textology testing extensions, and full QA requirements to meet commit standards. This version
has the highest library requirements, in order to match the versions used by Textology itself for testing. Required if
developing Textology itself, or recommended if looking to match/exceed the level of QA testing used by Textology.

### Extended Widgets

Native Textual widgets can be directly swapped out with Textology extended equivalents. They can then be used as is
(standard Textual usage), or with extensions (via extra keyword arguments).

- Basic swap (no extensions):
```python
# Replace:
from textual.widgets import Button

# With:
from textology.widgets import Button
```

- Instance callback extension (avoid global watchers and event chaining, repeat/temporary application, single/multiple)
  ```python
  from textology.widgets import Button
  
  button = Button(
      callbacks={Button.Pressed: lambda event: print("Don't press my buttons...")},
  )
  ```
  - <details>
    <summary>Callbacks can also be single fire (repeat false)</summary>
  
    ```python
    from textology.widgets import Button
    
    button = Button(
        callbacks={(Button.Pressed, False): lambda event: print("Don't press my buttons...")},
    )
    ```
  - <details>
    <summary>Callbacks can also be added via the handler name</summary>
  
    ```python
    from textology.widgets import Button
    
    button = Button(
        callbacks={"on_button_pressed": lambda event: print("Don't press my buttons...")},
    )
    ```
  - <details>
    <summary>Callbacks can also be added after instantiation</summary>
  
    ```python
    from textology.widgets import Button

    button = Button()
    button.add_callback(Button.Pressed, lambda event: print("Don't press my buttons..."))
    ```
  - <details>
    <summary>Callbacks can also be added for exceptions</summary>
  
    ```python
    from textology.widgets import Button

    button = Button()
    button.add_callback(ValueError, lambda exception: print("This error had exceptional value..."))
    ```


- Instance style extension (set styles directly at instantiation based on logic):
```python
from textology.widgets import Button

feeling_blue = True

button = Button(
    styles={
        "background": "blue" if feeling_blue else "green",
    },
)
```

- Instance message disable extension (avoid unused event chains, such as in large ListViews):
```python
from textual import events
from textology.widgets import ListItem

item = ListItem(
    disabled_messages=[events.Mount, events.Show],
)
```

### Extended Applications

Textology App classes, such as `WidgetApp`, can replace any regular Textual App, and be used as is without any
extensions turned on. Here are examples of the most commonly used application subclasses, `WidgetApp` and
`ExtendedApp`, and their primary extended functionality being used. More detailed examples of applications based
around routes, callbacks, and standard Textual applications can be found in [Examples](https://github.com/pyranha-labs/textology/examples).

- Basic App without subclassing:

  ```python
  from textology.apps import WidgetApp
  from textology.widgets import Button, Container, Label
  
  app = WidgetApp(
      Container(
          Button("Ping", callbacks={
              Button.Pressed: lambda event: app.query_one('#label').update("Ping")
          }),
          Button("Pong", callbacks={
              Button.Pressed: lambda event: app.query_one('#label').update("Pong")
          }),
          Button("Sing-a-long", callbacks={
              Button.Pressed: lambda event: app.query_one('#label').update("Sing-a-long")
          }),
          Label(id="label")
      )
  )
  app.run()
  ```

- Observer/callback application (automatic attribute monitoring and updates by element IDs without manual queries):

  ```python
  from textology.apps import ExtendedApp
  from textology.observers import Modified, Select, Update
  from textology.widgets import Button, Container, Label
  
  app = ExtendedApp(
      child=Container(
          Button("Ping", id="ping-btn"),
          Button("Pong", id="pong-btn"),
          Button("Sing-a-long", id="sing-btn"),
          Container(
              id="content",
          ),
      )
  )
  
  @app.when(
      Modified("ping-btn", "n_clicks"),
      Update("content", "children"),
  )
  def ping(clicks):
      return Label(f"Ping pressed {clicks}")
  
  @app.when(
      Modified("pong-btn", "n_clicks"),
      Update("content", "children"),
  )
  def pong(clicks):
      return Label(f"Pong pressed {clicks}")
  
  @app.when(
      Modified("sing-btn", "n_clicks"),
      Select("ping-btn", "n_clicks"),
      Select("pong-btn", "n_clicks"),
      Update("content", "children"),
  )
  def song(song_clicks, ping_clicks, pong_clicks):
      if not ping_clicks or not pong_clicks:
          return Label(f"Press Ping and Pong first to complete the song!")
      return Label(f"Ping, pong, sing-a-long song pressed {song_clicks}")
  
  app.run()
  ```

- Callbacks can also be async:
  ```python
  @app.when(
      Modified("pong-btn", "n_clicks"),
      Update("content", "children"),
  )
  async def delayed_pong(clicks):
      await asyncio.sleep(3)
      return Label(f"Pong pressed {clicks} and updated 3 seconds later")
  ```


- Callbacks can also catch Exceptions from other callbacks:
  ```python
  @app.when(
      Raised(Exception),
  )
  def error_notification(error):
      app.notify(f"An unknown error occurred: {error}", title="Error")
  ```

- <details>
  <summary>Callbacks can also listen for stateless events, not just stateful attribute updates</summary>

  ```python
  from textology.apps import ExtendedApp
  from textology.observers import Published, Select, Update
  from textology.widgets import Button, Container, Label
  
  app = ExtendedApp(
      child=Container(
          Button("Ping", id="ping-btn"),
          Button("Pong", id="pong-btn"),
          Button("Sing-a-long", id="sing-btn"),
          Container(
              id="content",
          ),
      )
  )
  
  @app.when(
      Published("ping-btn", Button.Pressed),
      Update("content", "children"),
  )
  def ping(event):
      return Label(f"Ping pressed {event.button.n_clicks}")
  
  @app.when(
      Published("pong-btn", Button.Pressed),
      Update("content", "children"),
  )
  def pong(event):
      return Label(f"Pong pressed {event.button.n_clicks}")
  
  @app.when(
      Published("sing-btn", Button.Pressed),
      Select("ping-btn", "n_clicks"),
      Select("pong-btn", "n_clicks"),
      Update("content", "children"),
  )
  def song(event, ping_clicks, pong_clicks):
      if not ping_clicks or not pong_clicks:
          return Label(f"Press Ping and Pong first to complete the song!")
      return Label(f"Ping, pong, sing-a-long song pressed {event.button.n_clicks}")
  
  app.run()
  ```

- <details>
  <summary>Callbacks can also be registered on methods, to share across all application instances</summary>

  ```python
  from textology.apps import ExtendedApp
  from textology.observers import Published, Select, Update, when
  from textology.widgets import Button, Container, Label
  
  class Page(Container):
      def compose(self):
          yield Button("Ping", id="ping-btn")
          yield Button("Pong", id="pong-btn")
          yield Button("Sing-a-long", id="sing-btn")
          yield Container(
              id="content",
          )
  
      @when(
          Published("ping-btn", Button.Pressed),
          Update("content", "children"),
      )
      def ping(self, event):
          return Label(f"Ping pressed {event.button.n_clicks}")
  
      @when(
          Published("pong-btn", Button.Pressed),
          Update("content", "children"),
      )
      def pong(self, event):
          return Label(f"Pong pressed {event.button.n_clicks}")
  
      @when(
          Published("sing-btn", Button.Pressed),
          Select("ping-btn", "n_clicks"),
          Select("pong-btn", "n_clicks"),
          Update("content", "children"),
      )
      def song(self, event, ping_clicks, pong_clicks):
          if not ping_clicks or not pong_clicks:
              return Label(f"Press Ping and Pong first to complete the song!")
          return Label(f"Ping, pong, sing-a-long song pressed {event.button.n_clicks}")
  
  app = ExtendedApp(
      child=Page()
  )
  
  app.run()
  ```

- <details>
  <summary>Callbacks can also use Dash code style (Same as others, but with Dash compatibility object and calls)</summary>

  ```python
  from textology.dash_compat import DashCompatApp, Input, Output, State
  from textology.widgets import Button, Container, Label
  
  app = DashCompatApp(
      layout=Container(
          Button("Ping", id="ping-btn"),
          Button("Pong", id="pong-btn"),
          Button("Sing-a-long", id="sing-btn"),
          Container(
              id="content",
          ),
      )
  )
  
  @app.callback(
      Input("ping-btn", "n_clicks"),
      Output("content", "children"),
  )
  def ping(clicks):
      return Label(f"Ping pressed {clicks}")
  
  @app.callback(
      Input("pong-btn", "n_clicks"),
      Output("content", "children"),
  )
  def pong(clicks):
      return Label(f"Pong pressed {clicks}")
  
  @app.callback(
      Input("sing-btn", "n_clicks"),
      State("ping-btn", "n_clicks"),
      State("pong-btn", "n_clicks"),
      Output("content", "children"),
  )
  def song(song_clicks, ping_clicks, pong_clicks):
      if not ping_clicks or not pong_clicks:
          return Label(f"Press Ping and Pong first to complete the song!")
      return Label(f"Ping, pong, sing-a-long song pressed {song_clicks}")
  
  app.run()
  ```

### Extended Testing

Don't want to serialize your pytests? Looking for the ability to quickly visualize differences when UIs change?
You came to the right place. Textology extends Textual SVG snapshot capabilities to add support for parallel processing
during tests (python-xdist), and custom options such as auto updating SVG snapshots on failures. In order to use the
pytest extensions automagically, add the following to a `conftest.py` in the root of the project. This will enable
usage of the `compare_snapshots` fixture, and HTML report generation on failure, automatically.

```python
pytest_plugins = ("textology.pytest_utils",)
```

- Basic snapshot test:
  ```python
  import pytest
  from textual import App
  from textual.widgets import Button
  
  class BasicApp(App):
      def compose(self):
          yield Button("Click me!")
  
  @pytest.mark.asyncio
  async def test_snapshot_with_app(compare_snapshots):
      assert await compare_snapshots(BasicApp())
  ```

Other advanced testing features include:
- Ability to pass an App, App Pilot, or a module containing an instantiated App or Pilot, to fixtures
- Custom snapshot paths, including reusing the same snapshot across multiple tests
- Automatic SVG updates with `pytest --txtology-snap-update`

View all options by running `pytest -h` and referring to `Custom options:` section.
