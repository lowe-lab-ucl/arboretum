import btrack
from napari.utils.colormaps import AVAILABLE_COLORMAPS

turbo = AVAILABLE_COLORMAPS['turbo']

def is_leaf(node):
    return len(node.children) >= 1


def _build_tree_graph(root, nodes):
    """ built the graph of the tree """

    max_generational_depth = max([n.generation for n in nodes])

    #put the start vertex into the queue, and the marked list
    queue = [root]
    marked = [root]
    y_pos = [0]

    # store the line coordinates that need to be plotted
    edges = []
    annotations = []
    markers = []

    # now step through
    while queue:
        # pop the root from the tree
        node = queue.pop(0)
        y = y_pos.pop(0)

        # TODO(arl): sync this with layer coloring
        depth = float(node.generation) / max_generational_depth
        edge_color = turbo[depth].RGB.tolist()[0]

        # draw the root of the tree
        edges.append(([y, y],
                      [node.t[0], node.t[-1]],
                      edge_color))
        markers.append((y, node.t[0],'k.'))

        # mark if this is an apoptotic tree
        if is_leaf(node):
            if node.fate == btrack.constants.Fates.APOPTOSIS:
                markers.append((y, node.t[-1], 'rx'))
                annotations.append((y, node.t[-1], str(node.ID), 'r'))
            else:
                markers.append((y, node.t[-1], 'ks'))
                annotations.append((y, node.t[-1], str(node.ID), 'w'))

        if node.is_root:
            annotations.append((y, node.t[0], str(node.ID), 'w'))

        children = [t for t in nodes if t.ID in node.children]

        for child in children:
            if child not in marked:

                # mark the children
                marked.append(child)
                queue.append(child)

                # calculate the depth modifier
                depth_mod = 2./(2.**(node.generation+1))

                if child == children[0]:
                    y_pos.append(y+depth_mod)
                else:
                    y_pos.append(y-depth_mod)

                # plot a linking line to the children
                edges.append(([y, y_pos[-1]], [node.t[-1], child.t[0]], 'w'))
                markers.append((y, node.t[-1],'go'))
                annotations.append((y_pos[-1],
                                    child.t[-1]-(child.t[-1]-child.t[0])/2.,
                                    str(child.ID), 'w'))


    # now that we have traversed the tree, calculate the span
    tree_span = []
    for edge in edges:
        tree_span.append(edge[0][0])
        tree_span.append(edge[0][1])

    # work out the span of the tree, we can modify positioning here
    min_x = min(tree_span)
    max_x = max(tree_span)

    return edges, markers, annotations
