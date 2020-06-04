import btrack
# from btrack.optimise.lineage import LineageTree
#
# def build_trees(tracks):
#     _recover_children(tracks)
#
#     trees = LineageTree(tracks)
#     trees.create()
#
#     return trees

# def _recover_children(tracks):
#     # # do a bit of tree processing, only needed for HDF import - needs to be
#     # sorted out in a release version
#     trees = {}
#     for trk in tracks:
#         if trk.root == 0:
#             trk.root = trk.ID
#
#         if trk.parent not in trees:
#             trees[trk.parent] = [trk.ID]
#         else:
#             trees[trk.parent].append(trk.ID)
#
#     for tree in trees:
#         if tree > 0:
#             trk = list(filter(lambda t: t.ID == tree, tracks))
#             if trk:
#                 trk[0].children = trees[tree]
#
#
# def generation(tree_manager, track):
#     """ get the generational depth of any track """
#     for tree in tree_manager.linear_trees:
#         node = [node for node in tree if node.track.ID == track.ID]
#         if node:
#             return node[0].depth
#     return 0



def _build_tree_graph(root_node, COLOR_CYCLE, color_by=None):
    """ built the graph of the tree """

    #put the start vertex into the queue, and the marked list
    queue = [root_node]
    marked = [root_node]
    y_pos = [0]

    # store the line coordinates that need to be plotted
    edges = []
    annotations = []
    markers = []

    # now step through
    while len(queue) > 0:
        # pop the root from the tree
        node = queue.pop(0)
        y = y_pos.pop(0)

        # draw the root of the tree
        edges.append(([y,y],
                      [node.start,node.end],
                      COLOR_CYCLE(color_by(node))*255))
        markers.append((y, node.start,'k.'))

        # mark if this is an apoptotic tree
        if node.leaf:
            if node.track.fate == btrack.constants.Fates.APOPTOSIS:
                markers.append((y, node.end, 'rx'))
                annotations.append((y, node.end, str(node.ID), 'r'))
            else:
                markers.append((y, node.end, 'ks'))
                annotations.append((y, node.end, str(node.ID), 'w'))

        if root_node.ID == node.ID:
            annotations.append((y, node.start, str(node.ID), 'w'))

        for child in node.children:
            if child not in marked:

                # mark the children
                marked.append(child)
                queue.append(child)

                # calculate the depth modifier
                depth_mod = 2./(2.**(node.depth-1.))

                if child == node.children[0]:
                    y_pos.append(y+depth_mod)
                else:
                    y_pos.append(y-depth_mod)

                # plot a linking line to the children
                edges.append(([y, y_pos[-1]], [node.end, child.start], 'w'))
                markers.append((y, node.end,'go'))
                annotations.append((y_pos[-1],
                                    child.end-(child.end-child.start)/2.,
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
