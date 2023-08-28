"""
Classes and functions for laying out graphs for visualisation.
"""
from __future__ import annotations

import itertools
from collections import Counter
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import numpy.typing as npt

from napari_arboretum.graph import TreeNode

# colormaps
WHITE = np.array([1.0, 1.0, 1.0, 1.0])

# minimum number of output edges to be considered a branching point
MIN_OUT_EDGES = 2

# napari specifies colours as a RGBA tuple in the range [0, 1], so mirror
# that convention throughout arboretum.
ColorType = npt.ArrayLike


@dataclass
class Annotation:
    x: float
    y: float
    label: str
    color: ColorType = field(default_factory=lambda: WHITE)


@dataclass
class Edge:
    x: tuple[float, float]
    y: tuple[float, float]
    color: ColorType = field(default_factory=lambda: WHITE)
    track_id: int | None = None
    node: TreeNode | None = None


def _find_merges(nodes: list[TreeNode]) -> dict[int, list[Any]]:
    node_ids = itertools.chain(*[n.children for n in nodes])
    merges = [n for n, count in Counter(node_ids).items() if count > 1]
    parents = [n for n in nodes if len(n.children) == 1]

    parent_merges: dict[int, list[TreeNode]] = {m: [] for m in merges}

    for merge in merges:
        parent_id = [p for p in parents if p.children[0] == merge]
        parent_merges[merge] += parent_id

    return parent_merges


def layout_tree(nodes: list[TreeNode]) -> tuple[list[Edge], list[Annotation]]:
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
    edges: list[Edge] = []
    annotations: list[Annotation] = []

    # iterate over the nodes and find merges
    merges = _find_merges(nodes)

    # now step through
    while queue:
        # pop the root from the tree
        node = queue.pop(0)
        y = y_pos.pop(0)

        # draw the root of the tree
        edges.append(
            Edge(y=(y, y), x=(node.t[0], node.t[-1]), track_id=node.ID, node=node)
        )

        if node.is_root:
            annotations.append(Annotation(y=y, x=node.t[0], label=str(node.ID)))

        # mark if this is an apoptotic tree
        if node.is_leaf:
            annotations.append(Annotation(y=y, x=node.t[-1], label=str(node.ID)))
            continue

        children = [t for t in nodes if t.ID in node.children]

        # calculate the depth modifier
        depth_mod = 2.0 / (2.0 ** (node.generation))
        spacing = np.linspace(-depth_mod, depth_mod, len(children))
        y_mod = spacing if len(children) > 1 else np.array([0.0])

        for idx, child in enumerate(children):
            if child.ID in merges:
                parents = merges[child.ID]
                parent_edges = [e for e in edges if e.node in parents]
                if len(parent_edges) < MIN_OUT_EDGES:
                    continue
                y_mod = np.asarray([np.mean([e.y[0] for e in parent_edges]) - y])

            if child not in marked:
                # mark the children
                marked.append(child)
                queue.append(child)

                y_pos.append(y + y_mod[idx])

                # if it's a leaf don't plot the annotation
                if not child.is_leaf:
                    annotations.append(
                        Annotation(
                            y=y_pos[-1],
                            x=child.t[-1] - (child.t[-1] - child.t[0]) / 2.0,
                            label=str(child.ID),
                        )
                    )

    # plot all of the hyperedges representing links, splits and merges
    hyperedges = filter(lambda e: e.node, edges)

    for hyperedge in hyperedges:
        children = hyperedge.node.children if hyperedge.node is not None else []
        childedges = filter(lambda e: e.track_id in children, edges)
        for childedge in childedges:
            edges.append(
                Edge(
                    y=(hyperedge.y[-1], childedge.y[0]),
                    x=(hyperedge.x[-1], childedge.x[0]),
                )
            )

    return edges, annotations
