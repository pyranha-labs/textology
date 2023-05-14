#!/usr/bin/env python3

"""Example of basic textual application with no textology extensions used."""

from textual.app import App
from textual.app import ComposeResult
from textual.containers import Container
from textual.containers import Horizontal
from textual.containers import Vertical
from textual.widgets import Label
from textual.widgets import ListItem
from textual.widgets import ListView


class SimpleApp(App):
    """Application with a listener for list view changes that will update content window using routes."""

    def compose(self) -> ComposeResult:
        """Primary content window."""
        label1 = Label("Page 1")
        label1.styles.color = "lightgreen"
        label2 = Label("Page 2")
        label2.styles.color = "yellow"
        label3 = Label("Page 3")
        label3.styles.color = "orange"

        main_menu_item1 = ListItem(label1)
        main_menu_item1.styles.height = 3
        main_menu_item1.styles.padding = 1
        main_menu_item2 = ListItem(label2)
        main_menu_item2.styles.height = 3
        main_menu_item2.styles.padding = 1
        main_menu_item3 = ListItem(label3)
        main_menu_item3.styles.height = 3
        main_menu_item3.styles.padding = 1
        main_menu = ListView(
            main_menu_item1,
            main_menu_item2,
            main_menu_item3,
            id="main-menu",
        )
        main_menu.styles.width = 24
        yield Horizontal(
            main_menu,
            Container(
                id="content",
            ),
        )

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        """Watch for all ListView highlight events, and update if it is the main menu changing."""
        if event.list_view and event.list_view.id == "main-menu":
            content = self.query_one("#content")
            content.remove_children()
            page = event.list_view.index + 1
            header = Label(f"Page {page}")
            header.styles.text_style = "bold"
            body = Label("Lorem ipsum dolor sit amet...")
            body.styles.color = "lightblue"
            sub_menu = ListView(
                ListItem(Label(f"Page {page} Item 1")),
                ListItem(Label(f"Page {page} Item 2")),
                ListItem(Label(f"Page {page} Item 3")),
                id="sub-menu",
            )
            sub_menu.styles.width = 20
            content.mount(
                Vertical(
                    header,
                    body,
                    sub_menu,
                )
            )


app = SimpleApp()


if __name__ == "__main__":
    app.run()
