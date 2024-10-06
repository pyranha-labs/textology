"""Extended Textual Tree widgets."""

from typing import Any
from typing import Iterable

from rich.highlighter import ReprHighlighter
from rich.text import Text
from rich.text import TextType
from textual import events
from textual import widgets
from textual.widgets.tree import TreeDataType
from textual.widgets.tree import TreeNode

from . import Tree
from ._extensions import Callbacks


class LazyTree(Tree):  # pylint: disable=too-many-ancestors
    """Widget to lazily render an interactive tree from a dataset.

    Content will be loaded as expanded to maximize performance.
    """

    def __init__(
        self,
        label: TextType,
        data: TreeDataType | None = None,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        styles: dict[str, Any] | None = None,
        disabled_messages: Iterable[type[events.Message]] | None = None,
        callbacks: Callbacks | None = None,
    ) -> None:
        """Initialize a Tree that will lazily render the data.

        Args:
            label: The label of the root node of the tree.
            data: The optional data to associate with the root node of the tree.
            name: The name of the Tree.
            id: The ID of the tree in the DOM.
            classes: The CSS classes of the tree.
            disabled: Whether the tree is disabled or not.
            styles: Local inline styles to apply on top of the class' styles for only this instance.
            disabled_messages: List of messages to disable on this widget instance only.
            callbacks: Mapping of callbacks to send messages to instead of sending to default handler.
        """
        super().__init__(
            label=label,
            data=data,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
            styles=styles,
            disabled_messages=disabled_messages,
            callbacks=callbacks,
        )
        self._highlighter = ReprHighlighter()
        self._initialized = {}

    def _initialize_node(self, node: TreeNode | None = None, recursive: bool = False) -> None:
        """Add contents for a node."""
        node = node or self.cursor_node
        if not self._initialized.get(id(node)) and node.allow_expand:
            data = node.data
            if isinstance(data, dict):
                for key, value in data.items():
                    label, allow_expand = self._get_node_config(key, value)
                    node.add(label, value, allow_expand=allow_expand)
            elif isinstance(data, list):
                for index, value in enumerate(data):
                    label, allow_expand = self._get_node_config(str(index), value)
                    node.add(label, value, allow_expand=allow_expand)
            self._initialized[id(node)] = True
        if recursive:
            for child in node.children:
                self._initialize_node(child, recursive=True)

    def _get_node_config(self, name: str, value: Any) -> tuple[Text, bool]:
        """Provide the configuration for a new node, such as the label and whether it can be expanded."""
        if isinstance(value, dict):
            allow_expand = True
            label = Text(f"{name}={{}}") if name else Text("{}")
        elif isinstance(value, list):
            allow_expand = True
            label = Text(f"{name}=[]") if name else Text("[]")
        else:
            allow_expand = False
            if name:
                label = Text.assemble(Text.from_markup(f"[b]{name}[/b]="), self._highlighter(repr(value)))
            else:
                label = Text(repr(value))
        return label, allow_expand

    async def _on_tree_node_expanded(self, event: widgets.Tree.NodeExpanded) -> None:
        """Lazily add the contents of the node after it is expanded."""
        self._initialize_node(event.node)

    def collapse_all(
        self,
        node: TreeNode | None = None,
    ) -> None:
        """Collapse a node and all the nodes below it.

        Args:
            node: The node to collapse. Defaults to selected node.
        """
        node = node or self.cursor_node
        if node:
            disabled = Tree.NodeCollapsed in self._disabled_messages
            if not disabled:
                self.disable_messages(Tree.NodeCollapsed)
            with self.app.batch_update():
                node.collapse_all()
            if not disabled:
                self.enable_messages(Tree.NodeCollapsed)

    def expand_all(
        self,
        node: TreeNode | None = None,
    ) -> None:
        """Expand a node and all the nodes below it.

        Lazy expansion is bypassed, immediately populating the entire branch.

        Args:
            node: The node to collapse. Defaults to selected node.
        """
        node = node or self.cursor_node
        if node:
            self._initialize_node(node, recursive=True)
            disabled = Tree.NodeExpanded in self._disabled_messages
            if not disabled:
                self.disable_messages(Tree.NodeExpanded)
            with self.app.batch_update():
                node.expand_all()
            if not disabled:
                self.enable_messages(Tree.NodeExpanded)
