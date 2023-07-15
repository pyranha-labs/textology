#! /usr/bin/env python

"""Static analysis tool for checking docstring conventions and style.

Patched to account for google convention not working properly due to numpy checks:
https://github.com/PyCQA/pydocstyle/issues/514
"""

from pydocstyle import cli
from pydocstyle.checker import ConventionChecker


def main() -> None:
    """Run pydocstyle after disabling numpy convention checking."""
    ConventionChecker.NUMPY_SECTION_NAMES = ()
    cli.main()


if __name__ == "__main__":
    main()
