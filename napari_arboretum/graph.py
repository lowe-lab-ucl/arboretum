"""
Classes and functions for working with graphs.

Note that this file should *not* contain code for laying out the graphs for
visualisation. Code for this is kept in `tree.py`.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Union

import napari
import numpy as np


@dataclass
class TreeNode:
    """TreeNode."""

    ID: int
    t: np.ndarray
    generation: int
    children: List[int] = field(default_factory=list)

    @property
    def is_root(self) -> bool:
        return self.generation == 1

    @property
    def is_leaf(self) -> bool:
        return not self.children

    def add_child(self, id: int, *, t_end: int):
        """
        Add a child to this node, and return the child.
        """
        child = TreeNode(id, (self.t[-1], t_end), self.generation + 1)
        self.children.append(id)
        return child


def build_reverse_graph(graph: dict) -> Tuple[Union[list, set], Dict[int, List[int]]]:
    """Take the data from a Tracks layer graph and reverse it.

    Parameters
    ----------
    graph : dict
        A dictionary encoding the graph, taken from the napari.Tracks layer.


    Returns
    -------
    roots : int, None
        A sorted list of integers represent the root node IDs
    reverse_graph : dict
        A reversed graph representing children of each parent node.
    """
    reverse_graph = {}
    roots: Set[int] = set()

    # iterate over the graph, reverse it and find the root nodes
    for node, parents in graph.items():
        for parent in parents:
            if parent not in reverse_graph:
                reverse_graph[parent] = [node]
            else:
                reverse_graph[parent].append(node)

            if parent not in graph.keys():
                roots.add(parent)

    # sort the roots
    sorted_roots = sorted(list(roots))

    return sorted_roots, reverse_graph


def linearise_tree(graph: dict, root: int) -> list:
    """Linearise a tree, i.e. return a list of track objects in the tree, but
    discard the heirarchy.

    Parameters
    ----------
    graph : dict
        A dictionary encoding the graph, taken from the napari.Tracks layer.
    root : int
        The root node to begin the search from.


    Returns
    -------
    linear : list
        A linearised tree, with only the node ID of each node of the tree.
    """
    queue = [root]
    linear = []
    while queue:
        node = queue.pop(0)
        linear.append(node)
        if node in graph:
            for child in graph[node]:
                queue.append(child)
    return linear


def get_root_id(layer: napari.layers.Tracks, search_node: int) -> int:
    """
    Get the root node of a given track ID.

    Parameters
    ----------
    layer :
        A napari tracks layer.
    search_node :
        The search node ID.

    Returns
    -------
    root_id :
        The root node ID of the tree which contains the node.
    """
    roots, reverse_graph = build_reverse_graph(layer.graph)
    linear_trees = [linearise_tree(reverse_graph, root) for root in roots]

    root_id = search_node
    for root, tree in zip(roots, linear_trees):
        if search_node in tree:
            root_id = root

    return root_id


def build_subgraph(layer: napari.layers.Tracks, search_node: int) -> List[TreeNode]:
    """Build a subgraph containing the node.

    The search node may not be the root of a tree, therefore, this function
    searches the whole graph to find a subgraph (tree) that contains the search
    node.

    Parameters
    ----------
    layer :
        A tracks layer.
    search_node :
        The search node ID. Note that this may not be the root of the tree,
        therefore, we need to search all branches of all trees to find this.

    Returns
    -------
    nodes :
        The nodes of the subtree that contain the search node.
    """
    _, reverse_graph = build_reverse_graph(layer.graph)
    root_id = get_root_id(layer, search_node)

    def _node_from_graph(_id):

        idx = np.where(layer.data[:, 0] == _id)[0]
        # t = (np.min(layer.data[idx, 1]), np.max(layer.data[idx, 1]))
        t = layer.data[idx, 1]
        node = TreeNode(ID=_id, t=t, generation=1)

        if _id in reverse_graph:
            node.children = reverse_graph[_id]

        return node

    # now build the treenode objects
    nodes = [_node_from_graph(root_id)]
    marked = [root_id]

    queue = [nodes[0]]

    # breadth first search
    while queue:
        node = queue.pop(0)
        for child in node.children:
            if child not in marked:
                marked.append(child)
                child_node = _node_from_graph(child)
                child_node.generation = node.generation + 1
                queue.append(child_node)
                nodes.append(child_node)

    return nodes
