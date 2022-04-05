from typing import List

import napari
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QVBoxLayout, QWidget

from .visualisation import PyQtGraphPlotter, TreePlotterQWidgetBase

GUI_MAXIMUM_WIDTH = 600


class Arboretum(QWidget):
    """
    Tree viewer widget.
    """

    def __init__(self, viewer: napari.Viewer, parent=None):
        super().__init__(parent=parent)
        self.viewer = viewer
        self.plotter: TreePlotterQWidgetBase = PyQtGraphPlotter()

        # build the canvas to display the trees
        layout = QVBoxLayout()
        layout.addWidget(self.plotter.get_qwidget())
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(4)
        self.setMaximumWidth(GUI_MAXIMUM_WIDTH)
        self.setLayout(layout)

        # hook up an event to update the list of tracks layers if the layer
        # list changes
        self.viewer.layers.events.changed.connect(self.update_tracks_layers)
        self.tracks_layers: List[napari.layers.Tracks] = []
        self.update_tracks_layers()

    def update_tracks_layers(self, event=None) -> None:
        """
        Get the Tracks layers that are present in the viewer.
        """
        layers = [
            layer
            for layer in self.viewer.layers
            if isinstance(layer, napari.layers.Tracks)
        ]

        for layer in layers:
            if layer not in self.tracks_layers:
                # Add callback to draw graph when layer clicked
                self.append_mouse_callback(layer)
                # Add callback to change tree colours when layer colours changed
                layer.events.color_by.connect(self.plotter.plot_branches)

        self.tracks_layers = layers

    def append_mouse_callback(self, track_layer: napari.layers.Tracks) -> None:
        """
        Add a mouse callback to ``track_layer`` to draw the tree
        when the layer is clicked.
        """

        @track_layer.mouse_drag_callbacks.append
        def show_tree(layer, event):
            self.plotter.tracks = layer

            cursor_position = event.position
            track_id = layer.get_value(cursor_position, world=True)
            if not track_id:
                return

            self.plotter.draw_tree(track_id)
