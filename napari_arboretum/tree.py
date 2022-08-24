"""
Classes and functions for laying out graphs for visualisation.
"""
from dataclasses import dataclass
from typing import List, MutableSequence, Optional, Tuple

import numpy as np

from .graph import TreeNode

# colormaps
WHITE = np.array([1.0, 1.0, 1.0, 1.0])

# napari specifies colours as a RGBA tuple in the range [0, 1], so mirror
# that convention throughout arboretum.
ColorType = MutableSequence[float]


@dataclass
class Annotation:
    x: float
    y: float
    label: str
    color: ColorType = WHITE


@dataclass
class Edge:
    x: Tuple[float, float]
    y: Tuple[float, float]
    color: np.ndarray = WHITE
    id: Optional[int] = None
    node: Optional[TreeNode] = None


def layout_tree(nodes: List[TreeNode]) -> Tuple[List[Edge], List[Annotation]]:
    """Build and layout the edges of a lineage tree, given the graph nodes.

    Parameters
    ----------
    nodes :
        A list of graph.TreeNode objects encoding a single lineage tree.

    Returns
    -------
    edges :
        A list of edges to be drawn.
    annotations :
        A list of annotations to be added to the graph.
    """
    # put the start vertex into the queue, and the marked list
    root = nodes[0]

    queue = [root]
    marked = [root]
    y_pos = [0.0]

    # store the line coordinates that need to be plotted
    edges = []
    annotations = []

    # now step through
    while queue:

        # pop the root from the tree
        node = queue.pop(0)
        y = y_pos.pop(0)

        # draw the root of the tree
        edges.append(Edge(y=(y, y), x=(node.t[0], node.t[-1]), id=node.ID, node=node))

        if node.is_root:
            annotations.append(Annotation(y=y, x=node.t[0], label=str(node.ID)))

        # mark if this is an apoptotic tree
        if node.is_leaf:
            annotations.append(Annotation(y=y, x=node.t[-1], label=str(node.ID)))
            continue

        children = [t for t in nodes if t.ID in node.children]

        for child in children:
            if child not in marked:

                # mark the children
                marked.append(child)
                queue.append(child)

                # calculate the depth modifier
                depth_mod = 2.0 / (2.0 ** (node.generation))

                if child == children[0]:
                    y_pos.append(y + depth_mod)
                else:
                    y_pos.append(y - depth_mod)

                # plot a linking line to the children
                edges.append(Edge(y=(y, y_pos[-1]), x=(node.t[-1], child.t[0])))

                # if it's a leaf don't plot the annotation
                if child.is_leaf:
                    continue

                annotations.append(
                    Annotation(
                        y=y_pos[-1],
                        x=child.t[-1] - (child.t[-1] - child.t[0]) / 2.0,
                        label=str(child.ID),
                    )
                )

    return edges, annotations
