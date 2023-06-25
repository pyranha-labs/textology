<div align="center">
  <img src="https://github.com/dfrtz/textology/blob/main/docs/banner.svg" width="450">
</div>

-----------------


[![os: windows mac linux](https://img.shields.io/badge/os-linux_|_macos_|_windows-blue)](https://docs.python.org/3.10/)
[![python: 3.10+](https://img.shields.io/badge/python-3.10_|_3.11-blue)](https://docs.python.org/3.10/)
[![python style: google](https://img.shields.io/badge/python%20style-google-blue)](https://google.github.io/styleguide/pyguide.html)
[![imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![code style: pycodestyle](https://img.shields.io/badge/code%20style-pycodestyle-green)](https://github.com/PyCQA/pycodestyle)
[![doc style: pydocstyle](https://img.shields.io/badge/doc%20style-pydocstyle-green)](https://github.com/PyCQA/pydocstyle)
[![static typing: mypy](https://img.shields.io/badge/static_typing-mypy-green)](https://github.com/python/mypy)
[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/PyCQA/pylint)
[![testing: pytest](https://img.shields.io/badge/testing-pytest-yellowgreen)](https://github.com/PyCQA/pylint)
[![security: bandit](https://img.shields.io/badge/security-bandit-black)](https://github.com/PyCQA/bandit)
[![license: MIT](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)


# Textology

### The study of making interactive UIs with text.

Why should GUIs have all the fun? Textology helps create TUIs by extending the amazing functionality of
[Textual](https://github.com/Textualize/textual) and [Rich](https://github.com/Textualize/rich),
with design principles from other well known Python libraries and UI frameworks.

Commonly known as Text (or Terminal) User Interfaces, the goal of a TUI (Tooey) is to provide as close
as possible to a traditional GUI experience straight from a terminal. Why? Not all environments allow full graphical
library access, web access, etc. Specifically, Textology is inspired by the designs of frameworks such as
Dash/FastAPI/Flask and their use of routing, context managers, and observation patterns. Textology also receives
inspiration from other UI frameworks external to Python, such as iOS, Android, and Web frameworks. Most importantly
however, Textology is an extension of Textual: it does not replace Textual, but rather provides additional options
on top of the core framework.

Before using Textology, be comfortable with Textual. Textology is NOT a replacement for Textual, it is an
extension. Callbacks, widgets, screens, event lifecycles, etc., from Textual still apply to Textology extended
widgets and applications. For other advanced features, familiarity with Dash/FastAPI/Flask principles will help.
Examples are included for advanced features, such as callback based applications.


## Table Of Contents

  * [Compatibility](#compatibility)
  * [Key Features](#top-features)
  * [Getting Started](#getting-started)
    * [Installation](#installation)
    * [Extended Applications](#extended-applications)
    * [Extended Widgets](#extended-widgets)
    * [Extended Testing](#extended-testing)


## Compatibility

Textology follows [Textual Compatibility](https://github.com/Textualize/textual#compatibility) guidelines with one
exception: Python3.10 minimum requirement.


## Top Features

- Extended basic widgets, such as:
  - Buttons with ability to declare callbacks inline, and track click counts
  - ListItems with metadata objects and ability to disable event messages
- New widgets, such as:
  - ListItemHeaders (non-interactive ListItems)
  - HorizontalMenus (walkable list of ListViews with peeking at following lists)
- "Observer" application, with "event driven architecture" to detect changes and automatically update elements in UI.
- Enhanced testing support
  - Parallel tests via python-xdist
  - Custom testing arguments, such as updating snapshots on failures


## Getting Started

### Installation

Install Textology via pip:
```shell
pip install textology
```

For dev requirements, use the additional `[dev]` package, which installs Textual development tools and extra QA tools:
```shell
pip install textology[dev]
```

### Extended Applications

Some Textology app classes, such as `ObservedApp`, can replace any regular Textual App, and be used as is without any
extensions turned on. Here is an example of the most commonly used extended application, `ObservedApp`, and its
primary extended functionality being used. More detailed examples of applications based around routes, callbacks,
and standard Textual applications can be found in [Examples](https://github.com/dfrtz/textology/examples).

- Observer/callback application (automatic attribute monitoring and updates by element IDs without manual queries):
```python
from textology.apps import ObservedApp
from textology.observers import Modified, Select, Update
from textology.widgets import Button, Container, Label

class SimpleApp(ObservedApp):
    def compose(self):
        yield Container(
            Button('Ping', id='ping-btn'),
            Button('Pong', id='pong-btn'),
            Button('Sing-a-long', id='sing-btn'),
            Container(
                id="content",
            ),
        )

app = SimpleApp()

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

### Extended Widgets

Native Textual widgets can be directly swapped out with Textology extended equivalents. They can then be used as is
(standard Textual usage), or with extensions (via extra keyword arguments).

- Basic swap (no extensions):
```python
# Replace:
from textual.widgets import Button

# With
from textology.widgets import Button
```

- Instance callback extension (avoid global watchers, name/ID checks in the event watchers, and event chaining):
```python
from textology.widgets import Button

def on_click(event):
    print("Don't press my buttons...")

button = Button(
    on_button_pressed=on_click,
)
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
    disable_messages=[events.Mount, events.Show],
)
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

@pytest.mark.asyncio
async def test_snapshot_with_app(compare_snapshots) -> None:
    class BasicApp(App):
        def compose(self):
            yield Button("Click me!", id="btn")
    assert await compare_snapshots(BasicApp())
```

Other advanced testing features include:
- Ability to pass and App, App Pilot, or a module containing an instantiated App or Pilot, to fixtures
- Custom snapshot paths, including reusing the same snapshot across multiple tests
- Automatic SVG updates with `pytest --txtology-snap-update`

View all options by running `pytest -h` and referring to `Custom options:` section.
