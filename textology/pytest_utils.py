"""Utilities for helping run unit tests with pytest."""

import getpass
import json
import os
import platform
import sqlite3
import time
from dataclasses import dataclass
from datetime import datetime
from os import PathLike
from pathlib import Path
from types import ModuleType
from typing import Iterable
from typing import Protocol

import pytest
import pytest_asyncio
import textual
from pytest import FixtureRequest
from textual.app import App
from textual.pilot import Pilot
from textual.widget import Widget

from textology import __version__
from textology import awaitables

OPT_SNAP_REPORT = "--txtology-snap-report"
OPT_SNAP_ROOT = "--txtology-snap-root"
OPT_SNAP_TEMPLATE = "--txtology-snap-template"
OPT_SNAP_UPDATE = "--txtology-snap-update"

TXTOLOGY_SNAPSHOTS = pytest.StashKey[list]()


class CompareSnapshotsFixture(Protocol):
    """Pytest fixture to automate user actions, snapshot/screenshot the application, and compare the results."""

    async def __call__(
        self,
        app_or_pilot_or_module: App | Pilot | ModuleType | None = None,
        compare_to: str | PathLike | None = None,
        test_suffix: str | None = None,
        press: Iterable[str] = (),
        click: list[type[Widget] | str | None] = (),
        run: awaitables.Runnable | list[awaitables.Runnable] | None = None,
        snap_title: str = None,
        wait_for_animation: bool = True,
        compare_results: bool = False,
    ) -> bool:
        """Fixture to automate user actions, snapshot/screenshot the application, and compare the results.

        See "compare_snapshots()" for more information.

        Args:
            app_or_pilot_or_module: Application, application test pilot, or module containing either.
            compare_to: Path to a saved snapshot.
                Defaults to: <directory of test file>/snapshots/<name of test>.py
            test_suffix: Optional suffix to add to the snapshot image name after the name of the test.
                Mutually exclusive with "compare_to" full path being provided.
            press: Key presses to run before waiting for animations to complete.
            click: Selectors to specify widgets that should be used as the reference for the click offset.
            run: One or more optional functions or futures to execute before taking the snapshot.
            snap_title: The title of the exported screenshot or None to use app title.
            wait_for_animation: Whether to wait for animations to complete before returning.
            compare_results: Compare all snapshots that have been generated with this session's fixture.

        Returns:
            True if the saved snapshot matches the new snapshot, false otherwise.

        Raises:
            AssertionError: If "compare_results" is used and one or more snapshots do not match saved values.
        """


@dataclass
class SnapshotFailure:
    """Class for keeping track of a single snapshot failure in a test."""

    pilot: Pilot
    result: bool = False
    result_svg: str | None = None
    expected_svg: str | None = None
    expected_path: str | None = None


async def auto_pilot(
    pilot: Pilot,
    press: Iterable[str] = (),
    click: list[type[Widget] | str | None] = (),
    run: awaitables.Runnable | list[awaitables.Runnable] | None = None,
    wait_for_animation: bool = True,
) -> None:
    """Automate user actions with an application test pilot.

    Args:
        pilot: Active test pilot for an application.
        press: Key presses to run before waiting for animations to complete.
        click: Selectors to specify widgets that should be used as the reference for the click offset.
        run: One or more optional functions or futures to execute.
        wait_for_animation: Whether to wait for animations to complete before returning.
    """
    await pilot.pause()
    await pilot.press(*press)
    for selector in click:
        await pilot.click(selector)
    if run:
        await awaitables.gather(*run)
    if wait_for_animation:
        await pilot.wait_for_scheduled_animations()
        await pilot.pause()


async def capture_snapshot(
    pilot: Pilot,
    press: Iterable[str] = (),
    click: list[type[Widget] | str | None] = (),
    run: awaitables.Runnable | list[awaitables.Runnable] | None = None,
    snap_title: str = None,
    wait_for_animation: bool = True,
) -> str:
    """Automate user actions, and then snapshot/screenshot the application.

    Args:
        pilot: Active test pilot for an application.
        press: Key presses to run before waiting for animations to complete.
        click: Selectors to specify widgets that should be used as the reference for the click offset.
        run: One or more optional functions or futures to execute before taking the snapshot.
        snap_title: The title of the exported screenshot or None to use app title.
        wait_for_animation: Whether to wait for animations to complete before returning.

    Returns:
        SVG screenshot of the current screen.
    """
    await auto_pilot(pilot, press=press, click=click, run=run, wait_for_animation=wait_for_animation)
    svg = pilot.app.export_screenshot(title=snap_title)
    return svg


async def compare_snapshots(  # pylint: disable=too-many-arguments
    request: FixtureRequest,
    pilot: Pilot,
    compare_to: str | PathLike | None = None,
    test_suffix: str | None = None,
    press: Iterable[str] = (),
    click: list[type[Widget] | str | None] = (),
    run: awaitables.Runnable | list[awaitables.Runnable] | None = None,
    snap_title: str = None,
    wait_for_animation: bool = True,
) -> tuple[bool, Path]:
    """Automate user actions, snapshot/screenshot the application, and compare the results.

    Compare a saved snapshot/screenshot of an application with a screenshot of the active application.
    When the snapshot update argument is used with pytest, the new snapshot will be saved if the test fails.
    New screenshots should only be permanently saved if manually validated to be correct.

    Args:
        request: Access to the requesting test context.
        pilot: Active test pilot for an application.
        compare_to: Path to a saved snapshot.
            Defaults to: <directory of test file>/snapshots/<name of test>.svg
        test_suffix: Optional suffix to add to the snapshot image name after the name of the test.
            Mutually exclusive with "compare_to" full path being provided.
        press: Key presses to run before waiting for animations to complete.
        click: Selectors to specify widgets that should be used as the reference for the click offset.
        run: One or more optional functions or futures to execute before taking the snapshot.
        snap_title: The title of the exported screenshot or None to use app title.
        wait_for_animation: Whether to wait for animations to complete before returning.

    Returns:
        True if the saved snapshot matches the new snapshot (false otherwise), and the final path to the snapshot.
    """
    if compare_to and test_suffix:
        raise ValueError("Cannot provide both a full compare_to path and test_suffix in snapshot tests")
    result_svg = await capture_snapshot(
        pilot,
        press=press,
        click=click,
        run=run,
        snap_title=snap_title,
        wait_for_animation=wait_for_animation,
    )

    expected_svg = None
    if not compare_to:
        image_name = request.node.name
        if test_suffix:
            image_name = f"{image_name}_{test_suffix}"
        compare_to = Path(request.fspath).parent / "snapshots" / f"{image_name}.svg"
    if os.path.exists(compare_to):
        expected_svg = Path(compare_to).read_text(encoding="UTF-8")

    result = result_svg == expected_svg
    if request.config.getoption(OPT_SNAP_UPDATE):
        failure_file = Path(compare_to)
        failure_file.parent.mkdir(parents=True, exist_ok=True)
        failure_file.write_text(result_svg, encoding="UTF-8")
        result = True

    node = request.node
    if result is False:
        node.stash[TXTOLOGY_SNAPSHOTS] = node.stash.get(TXTOLOGY_SNAPSHOTS, [])
        node.stash[TXTOLOGY_SNAPSHOTS].append(
            SnapshotFailure(
                pilot=pilot,
                result=result,
                result_svg=result_svg,
                expected_svg=expected_svg,
                expected_path=str(compare_to),
            )
        )
    return result, compare_to


@pytest_asyncio.fixture(name="compare_snapshots")
async def compare_snapshots_fixture(
    request: FixtureRequest,
) -> CompareSnapshotsFixture:
    """Pytest fixture to automate user actions, snapshot/screenshot the application, and compare the results.

    See "compare_snapshots()" for more information. This is an alias to provide more direct access via pytest
    without the need to import the utilities manually, or pass along other pytest fixtures.

    Args:
        request: Access to the requesting test context.

    Returns:
        Generated fixture to allow reuse multiple times in the same test.
    """
    test_suffixes = []
    test_results = []

    async def _compare_snapshots(
        app_or_pilot_or_module: App | Pilot | ModuleType | None = None,
        compare_to: str | PathLike | None = None,
        test_suffix: str | None = None,
        press: Iterable[str] = (),
        click: list[type[Widget] | str | None] = (),
        run: awaitables.Runnable | list[awaitables.Runnable] | None = None,
        snap_title: str = None,
        wait_for_animation: bool = True,
        compare_results: bool = False,
    ) -> bool:
        """Generated fixture to automate user actions, snapshot/screenshot the application, and compare the results.

        See "compare_snapshots()" or "CompareSnapshotsFixture" for more information. This is an alias to provide
        direct access via pytest without the need to import the utilities manually, or pass along other pytest fixtures.
        """
        nonlocal test_suffixes
        nonlocal test_results
        if app_or_pilot_or_module is not None:
            if isinstance(app_or_pilot_or_module, ModuleType):
                for var_name in dir(app_or_pilot_or_module):
                    var = getattr(app_or_pilot_or_module, var_name)
                    if isinstance(var, (App, Pilot)):
                        app_or_pilot_or_module = var
                        break

            if not compare_to and not test_suffix and len(test_suffixes) > 0 and None in test_suffixes:
                # Create an auto-incremented suffix to ensure a unique file is created when multiple snapshots are taken.
                test_suffix = f"snap_{len(test_suffixes) + 1}"
            test_suffixes.append(test_suffix)

            if not isinstance(app_or_pilot_or_module, Pilot):
                async with app_or_pilot_or_module.run_test() as pilot:
                    test_results.append(
                        await compare_snapshots(
                            request,
                            pilot,
                            compare_to=compare_to,
                            test_suffix=test_suffix,
                            press=press,
                            click=click,
                            run=run,
                            snap_title=snap_title,
                            wait_for_animation=wait_for_animation,
                        )
                    )
            else:
                test_results.append(
                    await compare_snapshots(
                        request,
                        app_or_pilot_or_module,
                        compare_to=compare_to,
                        test_suffix=test_suffix,
                        press=press,
                        click=click,
                        run=run,
                        snap_title=snap_title,
                        wait_for_animation=wait_for_animation,
                    )
                )
        if compare_results:
            mismatched = [
                f"Snapshot {index}: {path.name}" for index, (matched, path) in enumerate(test_results) if not matched
            ]
            count = len(mismatched)
            assert not count, (
                f"{count} snapshot(s) did not match expected results. Mismatched snapshots:\n" + "\n".join(mismatched)
            )
        return test_results[-1][0]

    yield _compare_snapshots


def _snapshot_failure_factory(cur: sqlite3.Cursor, row: tuple) -> dict:
    """Factory to convert DB rows into dicts, and rehydrate special types."""
    fields = [column[0] for column in cur.description]
    result = dict(zip(fields, row))
    result["app"] = json.loads(result["app"])
    return result


def _get_session_root(session: pytest.Session) -> Path:
    """Find the testing session root for storing reports and shared results when run via parallel processing."""
    root_opt = session.config.getoption(OPT_SNAP_ROOT)
    pytest_root = Path(root_opt) if root_opt else Path(session.config.rootdir) / ".pytest_textology"
    if not pytest_root.exists():
        pytest_root.mkdir(parents=True, exist_ok=True)
        (pytest_root / ".gitignore").write_text("# Created automatically by textology pytest plugin.\n*\n")
    return pytest_root


def pytest_addoption(parser: pytest.Parser) -> None:
    """Fixture function to add arguments to pytest to configure snapshot testing behaviors."""
    parser.addoption(
        OPT_SNAP_REPORT,
        action="store",
        help="Path to store the final HTML report with snapshot test results. Defaults to: <test root>/snapshot_test_report.html",
    )
    parser.addoption(
        OPT_SNAP_ROOT,
        action="store",
        help="Path to store snapshot testing files, such as reports and pytest shared worker results. Defaults to: <project root>/.pytest_textology",
    )
    parser.addoption(
        OPT_SNAP_TEMPLATE,
        action="store",
        help="Custom template to use for the HTML report with snapshot test results. Defaults to: textology/test-template.html",
    )
    parser.addoption(
        OPT_SNAP_UPDATE,
        action="store_true",
        help="Update snapshot files to the new test results if they do not match.",
    )


def pytest_sessionstart(
    session: pytest.Session,
) -> None:
    """Fixture function called before all pytest session(s) and test(s) are started.

    Executes multiple times when used with pytest-xdist: Once per parent pytest, and once per child pytest worker.
    Parent will create shared database for storing results, children will do nothing.

    Uses basic sqlite3 database for simple locking between processes.
    """
    if getattr(session.config, "workerinput", None) is not None:
        # This is a worker process, do not set up shared cache.
        return

    session_root = _get_session_root(session)
    with sqlite3.connect(session_root / "items.db") as con:
        cur = con.cursor()
        cur.execute("DROP TABLE IF EXISTS snapshot_failures")
        cur.execute(
            "CREATE TABLE snapshot_failures("
            "path varchar,"
            "name varchar,"
            "line int,"
            "result varchar,"
            "expected varchar,"
            "expectedPath varchar,"
            "app json"
            ")"
        )


def pytest_sessionfinish(
    session: pytest.Session,
    exitstatus: int,
) -> None:
    """Fixture function called after all pytest session(s) and test(s) are complete.

    Executes multiple times when used with pytest-xdist: Once per parent pytest, and once per child pytest worker.
    Parent will create and save final report, children will only store their test results.

    Uses basic sqlite3 database for simple locking between processes.
    """
    session_root = _get_session_root(session)
    if hasattr(session, "items"):
        with sqlite3.connect(session_root / "items.db") as con:
            cursor = con.cursor()
            for item in session.items:
                for snapshot in item.stash.get(TXTOLOGY_SNAPSHOTS, []):
                    if snapshot.result:
                        continue
                    _write_snapshot_failure(item, snapshot, cursor)
            con.commit()

    if getattr(session.config, "workerinput", None) is not None:
        # This is a worker process, no further action should be performed since session is not shared.
        return

    with sqlite3.connect(session_root / "items.db") as con:
        con.row_factory = _snapshot_failure_factory
        cursor = con.cursor()
        failures = cursor.execute("SELECT * FROM snapshot_failures").fetchall()

    if failures:
        final_result = {
            "timestamp": str(datetime.utcnow()),
            "exitstatus": exitstatus,
            "environment": {
                "cpus": os.cpu_count(),
                "cwd": os.getcwd(),
                "host": platform.node(),
                "platform": platform.platform(),
                "timezone": time.strftime("%z", time.gmtime()),
                "user": getpass.getuser(),
                "processor": platform.processor(),
            },
            "libraries": {
                "pytest": pytest.__version__,
                "pytest_asyncio": pytest_asyncio.__version__,
                "textology": __version__,
                "textual": textual.__version__,
            },
            "python": {
                "compiler": platform.python_compiler(),
                "implementation": platform.python_implementation(),
                "version": platform.python_version(),
            },
            "items": sorted(failures, key=lambda test: test.get("name")),
        }

        template_path_opt = session.config.getoption(OPT_SNAP_TEMPLATE)
        if template_path_opt:
            template = Path(template_path_opt).read_text(encoding="UTF-8")
        else:
            template = Path(os.path.dirname(__file__), "test-template.html").read_text(encoding="UTF-8")
        report = template.replace(
            'let testResult = "DUMMIES";',
            f"let testResult = {json.dumps(final_result, indent=4, default=str)};",
        )

        report_path_opt = session.config.getoption(OPT_SNAP_REPORT)
        report_path = Path(report_path_opt) if report_path_opt else Path(session_root / "snapshot_test_report.html")
        report_path.write_text(report, encoding="utf-8")

        session.config.txtology_report_path = report_path
        session.config.txtology_report_count = len(failures)


def pytest_terminal_summary(
    terminalreporter: "pytest.TerminalReporter",
    exitstatus: int,  # Match pytest arguments. pylint: disable=unused-argument
    config: pytest.Config,
) -> None:
    """Fixture function called before pytest exits to add a section to terminal summary about snapshot test results."""
    if hasattr(config, "txtology_report_path"):
        terminalreporter.ensure_newline()
        terminalreporter.section(
            f"{config.txtology_report_count} snapshot(s) did not match stored results",
            sep="=",
            red=True,
            bold=True,
        )
        terminalreporter.line(
            "Open the following link in browser for full details:\n"
            f"file://{config.txtology_report_path}\n"
            "\n"
            "If the new snapshots are correct, rerun using the following syntax to update the saved files:\n"
            f"pytest {OPT_SNAP_UPDATE}"
        )


def _write_snapshot_failure(item: pytest.Item, snapshot: SnapshotFailure, cursor: sqlite3.Cursor) -> None:
    """Save a snapshot test result from a worker process to a shared database table."""
    path, line_index, name = item.reportinfo()
    app = snapshot.pilot.app
    cursor.execute(
        "INSERT INTO snapshot_failures VALUES ("
        ":path,"
        ":name,"
        ":line,"
        ":result,"
        ":expected,"
        ":expectedPath,"
        ":app)",
        {
            "path": str(path),
            "name": name,
            "line": line_index + 1,
            "result": snapshot.result_svg,
            "expected": snapshot.expected_svg,
            "expectedPath": snapshot.expected_path,
            "app": json.dumps(
                {
                    "title": app.title,
                    "python_class": str(app.__class__),
                    "driver_class": str(app.driver_class),
                    "classes": " ".join(cls for cls in app.classes) if app.classes else "",
                    "css_path": app.css_path,
                    "console": {
                        "size": app.console.size,
                    },
                },
                default=str,
            ),
        },
    )
