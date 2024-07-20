#!/usr/bin/env python3

"""More advanced example of set up for a textual application with inline callbacks, instead of app wide callbacks."""

from textual.app import App
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.containers import Vertical

from textology.widgets import Container
from textology.widgets import Label
from textology.widgets import ListItem
from textology.widgets import ListView


class SimpleApp(App):
    """Application with a listener for list view changes that will update content window using routes."""

    def compose(self) -> ComposeResult:
        """Primary content window."""
        menu_item_styles = {"height": 3, "padding": 1}
        yield Horizontal(
            ListView(
                ListItem(Label("Page 1", styles={**menu_item_styles, "color": "lightgreen"}), data=1),
                ListItem(Label("Page 2", styles={**menu_item_styles, "color": "yellow"}), data=2),
                ListItem(Label("Page 3", styles={**menu_item_styles, "color": "orange"}), data=3),
                id="main-menu",
                styles={"width": 24},
                callbacks={
                    ListView.Highlighted: self.on_main_menu_highlighted,
                },
            ),
            Container(
                id="content",
            ),
        )

    def on_main_menu_highlighted(self, event: ListView.Highlighted) -> None:
        """Watch for all ListView highlight events, and update if it is the main menu changing."""
        if event.item:
            item = event.item
            content = self.query_one("#content")
            content.remove_children()
            content.mount(
                Vertical(
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
            )


app = SimpleApp()

if __name__ == "__main__":
    app.run()
