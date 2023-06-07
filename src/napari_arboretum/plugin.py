from __future__ import annotations

import napari
from napari.layers import Tracks
from napari.utils.events import Event
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QFileDialog, QGridLayout, QLabel, QPushButton, QWidget

from napari_arboretum.graph import get_root_id
from napari_arboretum.io.svg import export_svg
from napari_arboretum.util import TrackPropertyMixin
from napari_arboretum.visualisation.base_plotter import (
    PropertyPlotterBase,
    TreePlotterQWidgetBase,
)
from napari_arboretum.visualisation.matplotlib_plotter import MPLPropertyPlotter
from napari_arboretum.visualisation.vispy_plotter import VisPyPlotter

GUI_MAXIMUM_WIDTH = 500


class Arboretum(QWidget, TrackPropertyMixin):
    """
    Tree viewer widget.
    """

    def __init__(self, viewer: napari.Viewer = None, parent=None):
        super().__init__(parent=parent)
        viewer = napari.current_viewer() if viewer is None else viewer
        self.viewer = viewer
        self.title = QLabel()
        self.plotter: TreePlotterQWidgetBase = VisPyPlotter()
        self.property_plotter: PropertyPlotterBase = MPLPropertyPlotter(viewer)
        self.setMaximumWidth(GUI_MAXIMUM_WIDTH)

        # Set plugin layout
        layout = QGridLayout()

        row, col = 0, 0
        # Add title
        layout.addWidget(self.title, row, col, Qt.AlignHCenter)
        self.title.setText("Arboretum")

        # Add tree plotter
        row = 1
        layout.addWidget(self.plotter.get_qwidget(), row, col)
        # Add export button
        row = 2
        self.export_button = QPushButton("Export tree as SVG")
        layout.addWidget(self.export_button, row, col)
        # Add property plotter
        row = 3
        layout.addWidget(self.property_plotter.get_qwidget(), row, col)
        # Make the tree plot a bigger than the property plot
        for row, stretch in zip([1, 2, 3], [4, 1, 2]):
            layout.setRowStretch(row, stretch)
        self.setLayout(layout)

        # Update the list of tracks layers stored in this object if the layer
        # list changes
        self.viewer.layers.events.changed.connect(self.update_tracks_layers)
        # Update the horizontal time line if the current z-step changes
        self.viewer.dims.events.current_step.connect(self.draw_current_time_line)
        # Save the tree as an SVG
        self.export_button.clicked.connect(self.export_tree)

        self.tracks_layers: list[Tracks] = []
        self.update_tracks_layers()

    def on_tracks_change(self):
        self.plotter.tracks = self.tracks
        self.property_plotter.tracks = self.tracks

    def on_track_id_change(self):
        self.plotter.track_id = self.track_id
        self.property_plotter.track_id = self.track_id
        root_id = get_root_id(self.tracks, self.track_id)
        self.title.setText(f"Lineage Tree #{root_id}")

    def update_tracks_layers(self, event: Event | None = None) -> None:
        """
        Save a copy of all the tracks layers that are present in the viewer.
        """
        layers = [layer for layer in self.viewer.layers if isinstance(layer, Tracks)]

        for layer in layers:
            if layer not in self.tracks_layers:
                # Add callback to draw graph when layer clicked
                self.append_mouse_callback(layer)
                # Add callback to change tree colours when layer colours changed
                layer.events.color_by.connect(self.plotter.update_edge_colors)
                layer.events.colormap.connect(self.plotter.update_edge_colors)
                # Add callback to change 1D plotter plot when layer property changed
                layer.events.color_by.connect(self.property_plotter.plot_property)

        self.tracks_layers = layers

    def append_mouse_callback(self, track_layer: Tracks) -> None:
        """
        Add a mouse callback to ``track_layer`` to draw the tree
        when the layer is clicked.
        """

        @track_layer.mouse_double_click_callbacks.append
        def show_tree(tracks: Tracks, event: Event) -> None:
            self.tracks = tracks

            cursor_position = event.position
            track_id = tracks.get_value(cursor_position, world=True)
            if track_id is not None:
                # Setting this property automatically triggers re-drawing of the
                # tree and property graph
                self.track_id = track_id
                self.draw_current_time_line()

    def draw_current_time_line(self, event: Event | None = None) -> None:
        if not self.plotter.has_tracks:
            return
        z_value = self.viewer.dims.current_step[0]
        self.plotter.draw_current_time_line(z_value)
        self.property_plotter.draw_current_time_line(z_value)

    def export_tree(self) -> None:
        """Export the tree as an SVG."""
        root_id = get_root_id(self.tracks, self.track_id)
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export tree as SVG",
            f"tree_{root_id}.svg",
            "SVG Files(*.svg)",
            options=options,
        )
        if filename:
            export_svg(filename, self.plotter.edges, self.plotter.annotations)
