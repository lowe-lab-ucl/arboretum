# ------------------------------------------------------------------------------
# Name:     Arboretum
# Purpose:  Dockable widget, and custom track visualization layers for Napari,
#           to cell/object track data.
#
# Authors:  Alan R. Lowe (arl) a.lowe@ucl.ac.uk
#
# License:  See LICENSE.md
#
# Created:  01/05/2020
# ------------------------------------------------------------------------------
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Union

import numpy as np

from .tree import _build_tree


@dataclass
class TreeNode:
    """TreeNode."""

    ID: int
    t: Tuple[int, int]
    generation: int
    children: List["TreeNode"] = field(default_factory=list)

    def is_root(self) -> bool:
        return self.generation == 1

    def is_leaf(self) -> bool:
        return not self.children


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


def build_subgraph(layer, node):
    """Build a subgraph containing the node.

    The search node may not be the root of a tree, therefore, this function
    searches the whole graph to find a subgraph (tree) that contains the search
    node.

    Parameters
    ----------
    layer : napari.layers.Tracks
        A tracks layer.
    node : int
        The search node ID. Note that this may not be the root of the tree,
        therefore, we need to search all branches of all trees to find this.


    Returns
    -------
    root_id : int, None
        The root node ID of the tree which contains the node.
    nodes : list[TreeNode]
        The nodes of the subtree that contain the search node.
    """
    roots, reverse_graph = build_reverse_graph(layer.graph)
    linear_trees = [linearise_tree(reverse_graph, root) for root in roots]

    root_id = None
    for root, tree in zip(roots, linear_trees):
        if node in tree:
            root_id = root

    # if we did not find a root node, return None
    if root_id is None:
        return None, []

    def _node_from_graph(_id):

        idx = np.where(layer.data[:, 0] == _id)[0]
        t = (np.min(layer.data[idx, 1]), np.max(layer.data[idx, 1]))
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

    return root_id, nodes


def layout_subgraph(root_id, subgraph_nodes):
    return _build_tree(subgraph_nodes)
