"""Utilities for configuring and managing multi-page applications."""

from __future__ import annotations

import importlib
from types import ModuleType
from typing import Callable

_GLOBAL_PAGE_MAP: dict[str, Page] = {}


class Page:
    """Configuration for a page in a multi-page application routed via URL path."""

    def __init__(
        self,
        layout: Callable,
        path: str | None = None,
        name: str | None = None,
        order: int = 0,
        redirect_from: str | list[str] | None = None,
    ) -> None:
        """Initialize the page configuration.

        Args:
            layout: Function to call to generate the widget(s) used in the page's layout.
            path: URL Path, with or without variables. e.g. "/", "/home", "/documents/{document_name}"
                Inferred from the "layout" if not provided.
                    e.g. "home_page" -> "/home_page"
                Variables marked as {variable_name} in paths will be passed to "layout" as keyword arguments.
            name: The name of the page link, such as what might be shown in navigation menus.
                Inferred from the "path" if not provided.
                    e.g. "home_page" -> "Home Page"
            order: The relative order to sort pages in the "page_registry", such as ordering in navigation menus.
            redirect_from: Paths that should redirect to this page's path. e.g. "/v1/home"
        """
        if not path:
            path = layout.__name__.removeprefix("layout_")
        self.layout = layout
        self.path = path if path.startswith("/") else f"/{path}"
        self.name = name or self.path.strip("/").replace("_", " ").title()
        self.order = order
        self.redirect_from = [redirect_from] if isinstance(redirect_from, str) else redirect_from

    @staticmethod
    def from_module(module: ModuleType | str) -> Page:
        """Convert a module into an application page.

        Args:
            module: Loaded module, or path to a module, with page attributes such as "layout".

        Returns:
            Newly created page with attributes, such as path, populated by the module's attributes and variables.
        """
        kwargs = {}
        vars_to_save = ("layout", "path", "name", "order", "redirect_from")
        if isinstance(module, str):
            module = importlib.import_module(module)
        for var_name in dir(module):
            if var_name not in vars_to_save:
                continue
            var = getattr(module, var_name)
            kwargs[var_name] = var

        if "layout" not in kwargs:
            raise ValueError(f"Module {module} must contain a layout function to be used as a page")
        if "path" not in kwargs:
            kwargs["path"] = module.__name__.rsplit(".", 1)[-1]
        return Page(**kwargs)

    @staticmethod
    def to_page(page: Page | ModuleType | str | Callable) -> Page:
        """Convert a page compatible object into a full application page.

        Args:
            page: Object compatible with conversion into an application page, such as module, module name, for function.
                e.g. "modules" will create full pages after searching for all values compatible with Page.
                e.g. "functions" will only create a basic Page with the path based on name of the layout function.

        Returns:
            Newly created page with attributes, such as path, populated based on the type of object provided.
        """
        if isinstance(page, (ModuleType, str)):
            page = Page.from_module(page)
        elif isinstance(page, Callable):
            page = Page(page)
        return page


def register_page(  # pylint: disable=too-many-arguments
    page: Page | ModuleType | str | Callable | None = None,
    path: str | None = None,
    name: str | None = None,
    order: int = 0,
    redirect_from: str | list[str] | None = None,
    layout: Callable | None = None,
    page_map: dict[str, Page] | None = None,
) -> Page:
    """Register a URL path to a layout shared across all multi-page applications.

    Args:
        page: A module, or module path, where the remaining page's variables are defined.
            e.g. If calling from within the module itself: "__name__"
            e.g. If calling from another module: "mylib.home"
        path: URL Path, with or without variables. e.g. "/", "/home", "/documents/{document_name}"
            Inferred from the "module" or "layout" if not provided.
                e.g. "mylib.home" -> "/home"
                e.g. "layout_home_page" -> "/home_page"
            Variables marked as {variable_name} in paths will be passed to "layout" as keyword arguments.
        name: The name of the page link, such as what might be shown in navigation menus.
            Inferred from the "path" if not provided.
                e.g. "home_page" -> "Home Page"
        order: The relative order to sort pages in the "page_registry", such as ordering in navigation menus.
        redirect_from: Paths that should redirect to this page's path. e.g. "/v1/home"
        layout: Function to call to generate the widget(s) used in the page's layout.
        page_map: All currently registered pages for a multi-page app.
            Modified in place when page is registered. Defaults to global pages shared across apps.

    Returns:
        Final page registered to the path, and created from arguments if needed.
    """
    if not page and not layout:
        raise ValueError("Either a module or a layout must be provided to create a page")
    if isinstance(redirect_from, str):
        redirect_from = [redirect_from]
    if page is not None:
        page = Page.to_page(page)
        if path:
            page.path = path
        if redirect_from:
            page.redirect_from = redirect_from
        if layout:
            page.layout = layout
        if name:
            page.name = name
        if order:
            page.order = order
    else:
        page = Page(
            layout=layout,
            path=path,
            name=name,
            order=order,
            redirect_from=redirect_from,
        )
    paths = [page.path]
    if page.redirect_from:
        paths.extend(page.redirect_from)
    page_map = page_map if page_map is not None else _GLOBAL_PAGE_MAP
    for page_path in paths:
        if page.path in page_map:
            raise ValueError(f"Duplicate page found for path: {page_path}")
        page_map[page_path] = page
    return page
