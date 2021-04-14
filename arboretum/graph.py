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

import numpy as np

from .tree import _build_tree


class TreeNode:
    def __init__(self):
        self.ID = None
        self.t = ()
        self.generation = None
        self.children = []

    def is_root(self):
        return self.generation == 1

    def is_leaf(self):
        return not self.children


def build_reverse_graph(graph: dict) -> list:
    """Take the data from a Tracks layer graph and reverse it."""
    reverse_graph = {}
    roots = set()

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
    roots = sorted(list(roots))

    return roots, reverse_graph


def linearise_tree(graph, root):
    """Linearise a tree, i.e. return a list of track objects in the
    tree, but lose the heirarchy."""
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

    Parameters
    ----------

    layer : napari.layers.Tracks
        A tracks layer

    node : int
        The search node ID


    Returns
    -------

    root : int, None

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

        node = TreeNode()
        node.ID = _id

        idx = np.where(layer.data[:, 0] == _id)[0]
        node.t = (np.min(layer.data[idx, 1]), np.max(layer.data[idx, 1]))
        if _id in reverse_graph:
            node.children = reverse_graph[_id]
        node.generation = 1

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
