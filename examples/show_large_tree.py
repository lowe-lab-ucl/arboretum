"""
Show a large tree in arboretum
==============================
"""
from copy import copy

import napari

from napari_arboretum import Arboretum
from napari_arboretum.graph import TreeNode


def generate_binary_tree(max_depth: int):
    id = 0
    nodes = [TreeNode(id, t=(0, 1), generation=1)]
    for depth in range(1, max_depth):
        for node in copy(nodes):
            if node.generation == depth:
                for _ in range(2):
                    # Add two children
                    id += 1
                    new_node = node.add_child(id, t_end=node.t[-1] + 1)
                    nodes.append(new_node)
    return nodes


nodes = generate_binary_tree(8)
print(f"{len(nodes)} total nodes")


viewer = napari.Viewer()
_, widget = viewer.window.add_plugin_dock_widget(
    plugin_name="napari-arboretum", widget_name="Arboretum"
)
widget.plotter.draw_from_nodes(nodes)

if __name__ == '__main__':
    # The napari event loop needs to be run under here to allow the window
    # to be spawned from a Python script
    napari.run()
