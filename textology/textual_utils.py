"""Common utilities for interacting with the base textual module."""

from collections import namedtuple

from textual import __version__ as __lib_version__  # Dynamic attribute in textual. pylint: disable=no-name-in-module

TextualVersion = namedtuple("TextualVersion", ["major", "minor", "maintenance"])
major, minor, maintenance = __lib_version__.split(".")
major, minor, maintenance = int(major), int(minor), int(maintenance)

textual_version = TextualVersion(major, minor, maintenance)
