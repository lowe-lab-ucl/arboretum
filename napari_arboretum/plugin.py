from typing import List, Optional

import napari
from napari.utils.events import Event
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGridLayout, QWidget

from .visualisation import (
    MPLPropertyPlotter,
    PropertyPlotterBase,
    TreePlotterQWidgetBase,
    VisPyPlotter,
)

GUI_MAXIMUM_WIDTH = 400


class Arboretum(QWidget):
    """
    Tree viewer widget.
    """

    def __init__(self, viewer: napari.Viewer, parent=None):
        super().__init__(parent=parent)
        self.viewer = viewer
        self.plotter: TreePlotterQWidgetBase = VisPyPlotter()
        self.property_plotter: PropertyPlotterBase = MPLPropertyPlotter(viewer)

        # Set plugin layout
        layout = QGridLayout()
        # Make the tree plot a bigger than the property plot
        for row, stretch in zip([0, 1], [2, 1]):
            layout.setRowStretch(row, stretch)
        self.setLayout(layout)

        # Add tree plotter
        row, col = 0, 0
        layout.addWidget(self.plotter.get_qwidget(), row, col)
        # Add property plotter
        row = 1
        layout.addWidget(self.property_plotter.get_qwidget(), row, col)

        # Update the list of tracks layers stored in this object if the layer
        # list changes
        self.viewer.layers.events.changed.connect(self.update_tracks_layers)
        # Update the horizontal time line if the current z-step changes
        self.viewer.dims.events.current_step.connect(self.draw_current_time_line)

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
                layer.events.color_by.connect(self.plotter.update_edge_colors)
                layer.events.colormap.connect(self.plotter.update_edge_colors)
                layer.events.color_by.connect(self.property_plotter.plot_property)

        self.tracks_layers = layers

    def append_mouse_callback(self, track_layer: napari.layers.Tracks) -> None:
        """
        Add a mouse callback to ``track_layer`` to draw the tree
        when the layer is clicked.
        """

        @track_layer.mouse_drag_callbacks.append
        def show_tree(layer: napari.layers.Tracks, event: Event) -> None:
            self.plotter.tracks = layer
            self.property_plotter.tracks = layer

            cursor_position = event.position
            track_id = layer.get_value(cursor_position, world=True)
            if not track_id:
                return

            self.plotter.draw_tree(track_id)
            self.track_id = track_id
            self.property_plotter.track_id = track_id
            self.property_plotter.plot_property()

    def draw_current_time_line(self, event: Optional[Event] = None) -> None:
        if not self.plotter.has_tracks:
            return
        z_value = self.viewer.dims.current_step[0]
        self.plotter.draw_current_time_line(z_value)
