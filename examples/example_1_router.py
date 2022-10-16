#!/usr/bin/env python3

"""Basic example of set up and loop for a Router."""

from textology.router import Router

app = Router()


@app.route("/ping/{item}")
def ping_item(item: str) -> str:
    """Basic response."""
    return f"pong {item}"


while (path := input("Enter /ping/<value>, or /quit to exit: ")) != "/quit":
    print(app.serve(path))
