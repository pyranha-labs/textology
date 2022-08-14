# Textology

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

### The study of making interactive UIs with text.

Textology helps create TUIs by extending the amazing functionality of [Textual](https://github.com/Textualize/textual)
and [Rich](https://github.com/Textualize/rich), with design principles from other widely used Python libraries
and UI frameworks.

Commonly known as Terminal (Text) User Interfaces, or "Tooeys", the end goal of a TUI is to provide as close
as possible to a traditional GUI experience with only "text". Why? Because not all environments allow full graphical
library access, HTTP access, etc. Specifically, Textology is inspired by the work of Dash/FastAPI/Flask and their use
of routing, context managers, and observation patterns. Textology also receives inspiration from other UI frameworks
external to Python, such as iOS, Android, and Web frameworks.

Before using Textology, be comfortable with Textual. Textology is NOT a replacement for Textual, but rather an
extension. Callbacks, widgets, screens, event lifecycles, etc., from Textual still apply to Textology extended
applications. For other advanced features, be familiar with Dash/FastAPI/Flask principles.


## Compatability

Textology follows [Textual Compatibility](https://github.com/Textualize/textual#compatibility) guidelines with one
exception: Python3.10 minimum requirement.


## Key Features

- Extended basic widgets, such as Buttons with ability to declare callbacks inline, and ListItems with metadata objects.
- New widgets, such as ListItemHeaders (non-interactive ListItems), and HorizontalMenus (walkable list of ListViews).
- "Observer" application, with "event driven architecture" to detect changes and automatically update elements in UI.
- "Browser" application with history of addresses visited and ability to navigate forwards/backwards.


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

### Applications

Examples of basic applications based around routes, callbacks, and standard Textual applications can be found in
[Examples](./examples).
