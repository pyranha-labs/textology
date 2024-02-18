#!/usr/bin/env python3

"""More advanced example of set up and loop for router application, based on a textual application (Browser app)."""

from textual.containers import Horizontal
from textual.containers import Vertical
from textual.widget import Widget

from textology.apps import ExtendedApp
from textology.widgets import Container
from textology.widgets import Label
from textology.widgets import ListItem
from textology.widgets import ListView
from textology.widgets import Location


class SimpleApp(ExtendedApp):
    """Application with a listener for list view changes that will update content window using routes."""

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        """Watch for all ListView highlight events, and update if it is the main menu changing."""
        if event.list_view and event.list_view.id == "main-menu":
            result = self.location.get(f"/page/{event.item.data}")
            content = self.query_one("#content")
            content.remove_children()
            content.mount(result)


menu_item_styles = {"height": 3, "padding": 1}
app = SimpleApp(
    child=Horizontal(
        Location(id="url"),
        ListView(
            ListItem(Label("Page 1", styles={**menu_item_styles, "color": "lightgreen"}), data=1),
            ListItem(Label("Page 2", styles={**menu_item_styles, "color": "yellow"}), data=2),
            ListItem(Label("Page 3", styles={**menu_item_styles, "color": "orange"}), data=3),
            id="main-menu",
            styles={"width": 24},
        ),
        Container(
            id="content",
        ),
    )
)


@app.route("/page/{page}")
def with_request_and_variable(page: str) -> Widget:
    """Route that automatically receives the original request, and a user provided variable from the path."""
    return Vertical(
        Label(f"Page {page}", styles={"text_style": "bold"}),
        Label("Lorem ipsum dolor sit amet...", styles={"color": "lightblue"}),
        ListView(
            ListItem(Label(f"Page {page} Item 1")),
            ListItem(Label(f"Page {page} Item 2")),
            ListItem(Label(f"Page {page} Item 3")),
            id="sub-menu",
            styles={"width": 20},
        ),
    )


if __name__ == "__main__":
    app.run()
