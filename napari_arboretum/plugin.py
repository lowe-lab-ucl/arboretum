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

import napari
import pyqtgraph as pg
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QVBoxLayout, QWidget

from .graph import build_subgraph, layout_subgraph

GUI_MAXIMUM_WIDTH = 450


class Arboretum(QWidget):
    """Tree viewer widget.

    Parameters
    ----------
    viewer : napari.Viewer
        Accepts the napari viewer.


    Returns
    -------

    arboretum : QWidget
        The arboretum widget.

    """

    def __init__(self, viewer: "napari.viewer.Viewer", parent=None):
        super().__init__(parent=parent)

        # store a reference to the viewer
        self._viewer = viewer

        # build the canvas to display the trees
        layout = QVBoxLayout()
        plot_widget = pg.GraphicsLayoutWidget()
        self.plot_view = plot_widget.addPlot(
            title="Lineage tree", labels={"left": "Time"}
        )
        self.plot_view.hideAxis("bottom")
        layout.addWidget(plot_widget)
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(4)
        self.setMaximumWidth(GUI_MAXIMUM_WIDTH)
        self.setLayout(layout)

        # hook up an event to find Tracks layers if the layer list changes
        self._viewer.layers.events.changed.connect(self._get_tracks_layers)

        # store the tracks layers
        self._tracks_layers = []
        self._get_tracks_layers()

    def _get_tracks_layers(self, event=None):
        """Get the Tracks layers that are present in the viewer."""
        layers = [
            layer
            for layer in self._viewer.layers
            if isinstance(layer, napari.layers.Tracks)
        ]

        for layer in layers:
            if layer not in self._tracks_layers:
                self._append_mouse_callback(layer)

        self._tracks_layers = layers

    def _append_mouse_callback(self, layer: napari.layers.Tracks):
        """Append a mouse callback to each Tracks layer."""

        @layer.mouse_drag_callbacks.append
        def show_tree(layer, event):

            track_id = layer.get_value(layer.position)
            root, subgraph_nodes = build_subgraph(layer, track_id)

            if not subgraph_nodes:
                return

            edges, annotations = layout_subgraph(root, subgraph_nodes)
            self.draw_graph(track_id, edges, annotations)

    def draw_graph(self, track_id, edges, annotations):
        """Plot graph on the plugin canvas."""
        self.plot_view.clear()
        self.plot_view.setTitle(f"Lineage tree: {track_id}")

        for ex, ey, ec in edges:
            self.plot_view.plot(ex, ey, pen=pg.mkPen(color=ec, width=3))

        # labels
        for tx, ty, tstr, tcol in annotations:

            if tstr == str(track_id):
                tcol[3] = 255
            else:
                tcol[3] = 64

            pt = pg.TextItem(
                text=tstr,
                color=tcol,
                html=None,
                anchor=(0, 0),
                border=None,
                fill=None,
                angle=0,
                rotateAxis=None,
            )
            pt.setPos(tx, ty)
            self.plot_view.addItem(pt, ignoreBounds=True)
