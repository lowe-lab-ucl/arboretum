from dataclasses import dataclass
from typing import List, Optional, Tuple

import numpy as np
from napari.utils.colormaps import AVAILABLE_COLORMAPS

# colormaps
turbo = AVAILABLE_COLORMAPS["turbo"]
WHITE = np.array([1, 1, 1, 1], dtype=float)
RED = np.array([1, 0, 0, 1], dtype=float)

# napari specifies colours as a RGBA tuple in the range [0, 1], so mirror
# that convention throughout arboretum.
ColorType = Tuple[float, float, float, float]


@dataclass
class Annotation:
    x: float
    y: float
    label: str
    color: ColorType


@dataclass
class Edge:
    x: Tuple[float, float]
    y: Tuple[float, float]
    color: ColorType
    id: Optional[int] = None


def _build_tree(nodes) -> Tuple[List[Edge], List[Annotation]]:
    """Build and layout the edges of a lineage tree, given the graph nodes.

    Parameters
    ----------
    nodes : list
        A list of graph.TreeNode objects encoding a single lineage tree.

    Returns
    -------
    edges : list
        A list of edges to be drawn.

    annotations : list
        A list of annotations to be added to the graph.
    """

    max_generational_depth = max([n.generation for n in nodes])

    # put the start vertex into the queue, and the marked list

    root = nodes[0]

    queue = [root]
    marked = [root]
    y_pos = [0]

    # store the line coordinates that need to be plotted
    edges = []
    annotations = []

    # now step through
    while queue:

        # pop the root from the tree
        node = queue.pop(0)
        y = y_pos.pop(0)

        # TODO(arl): sync this with layer coloring
        depth = float(node.generation) / max_generational_depth
        edge_color = turbo.map(depth)[0]

        # draw the root of the tree
        edges.append(
            Edge(y=(y, y), x=(node.t[0], node.t[-1]), color=edge_color, id=node.ID)
        )

        # mark if this is an apoptotic tree
        if node.is_leaf:
            annotations.append(
                Annotation(y=y, x=node.t[-1], label=str(node.ID), color=WHITE)
            )

        if node.is_root:
            annotations.append(
                Annotation(y=y, x=node.t[0], label=str(node.ID), color=WHITE)
            )

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
                edges.append(
                    Edge(y=(y, y_pos[-1]), x=(node.t[-1], child.t[0]), color=WHITE)
                )
                annotations.append(
                    Annotation(
                        y=y_pos[-1],
                        x=child.t[-1] - (child.t[-1] - child.t[0]) / 2.0,
                        label=str(child.ID),
                        color=WHITE,
                    )
                )

    # now that we have traversed the tree, calculate the span
    tree_span = []
    for edge in edges:
        tree_span.append(edge.y[0])
        tree_span.append(edge.y[1])

    # # work out the span of the tree, we can modify positioning here
    # min_x = min(tree_span)
    # max_x = max(tree_span)

    return edges, annotations
