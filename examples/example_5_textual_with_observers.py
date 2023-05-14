#!/usr/bin/env python3

"""More advanced example of set up and loop for observer application, based on a textual application."""

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.containers import Vertical
from textual.widget import Widget

from textology.apps import ObservedApp
from textology.observers import Modified
from textology.observers import Update
from textology.widgets import Container
from textology.widgets import Label
from textology.widgets import ListItem
from textology.widgets import ListView


class SimpleApp(ObservedApp):
    """Application with a listener for list view changes that will update content window using routes."""

    def compose(self) -> ComposeResult:
        """Primary content window."""
        menu_item_styles = {"height": 3, "padding": 1}
        yield Horizontal(
            ListView(
                ListItem(
                    Label("Page 1", styles={**menu_item_styles, "color": "lightgreen"}),
                    data=1,
                ),
                ListItem(
                    Label("Page 2", styles={**menu_item_styles, "color": "yellow"}),
                    data=2,
                ),
                ListItem(
                    Label("Page 3", styles={**menu_item_styles, "color": "orange"}),
                    data=3,
                ),
                id="main-menu",
                styles={"width": 24},
            ),
            Container(
                id="content",
            ),
        )


app = SimpleApp()


@app.when(
    Modified("main-menu", "highlighted"),
    Update("content", "children"),
)
def update_content(item: ListItem) -> Widget:
    """Directly update the content on main menu change."""
    return Vertical(
        Label(f"Page {item.data}", styles={"text_style": "bold"}),
        Label("Lorem ipsum dolor sit amet...", styles={"color": "lightblue"}),
        ListView(
            ListItem(Label(f"Page {item.data} Item 1")),
            ListItem(Label(f"Page {item.data} Item 2")),
            ListItem(Label(f"Page {item.data} Item 3")),
            id="sub-menu",
            styles={"width": 20},
        ),
    )


if __name__ == "__main__":
    app.run()
