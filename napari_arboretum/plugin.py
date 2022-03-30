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

from typing import List

import napari
import numpy as np
import pyqtgraph as pg
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QVBoxLayout, QWidget

from .graph import build_subgraph, layout_subgraph

GUI_MAXIMUM_WIDTH = 600


class Arboretum(QWidget):
    """
    Tree viewer widget.

    Parameters
    ----------
    viewer : napari.Viewer
        Accepts the napari viewer.


    Returns
    -------
    arboretum : QWidget
        The arboretum widget.

    """

    def __init__(self, viewer: napari.Viewer, parent=None):
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
        self._tracks_layers: List[napari.layers.Tracks] = []
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
                layer.events.color_by.connect(self.draw_graph)

        self._tracks_layers = layers

    def _append_mouse_callback(self, layer: napari.layers.Tracks):
        """Append a mouse callback to each Tracks layer."""

        @layer.mouse_drag_callbacks.append
        def show_tree(layer, event):
            self.layer = layer

            # cursor_position = layer.position
            cursor_position = self._viewer.cursor.position

            # fix to return the track ID using the world coordinates returned
            # by `viewer.cursor.position`
            track_id = layer.get_value(cursor_position, world=True)

            if not track_id:
                return
            self.track_id = track_id

            root, subgraph_nodes = build_subgraph(layer, self.track_id)

            self.edges, self.annotations = layout_subgraph(root, subgraph_nodes)
            self.draw_graph()

    def update_colors(self):
        """
        Update colors on a list of edges from the colors they have in a
        track layer. Note that this updates the colors in-place on ``edges``.
        """
        for e in self.edges:
            if e.id is not None:
                color = self.layer.track_colors[
                    np.where(self.layer.properties["track_id"] == e.id)
                ][-1]
                # napari uses [0, 1] RGBA, pygraphqt uses [0, 255] RGBA
                e.color = color * 255

    def draw_graph(self):
        """
        Plot graph on the plugin canvas.

        Parameters
        ----------
        track_id : int
        edges : list[Edge]
            List containing individual edges.
        annotations : list[tuple[float, float, str, numpy.ndarray[int]]]
            Annotations to add. Each list item is a tuple with:
            - x coordinate
            - y coordinate
            - annoation text
            - color (in rgba form)
        """
        self.update_colors()

        self.plot_view.clear()
        self.plot_view.setTitle(f"Lineage tree: {self.track_id}")

        # NOTE(arl): disabling the autoranging improves perfomance dramatically
        # https://stackoverflow.com/questions/17103698/plotting-large-arrays-in-pyqtgraph
        self.plot_view.disableAutoRange()

        for e in self.edges:
            self.plot_view.plot(e.y, e.x, pen=pg.mkPen(color=e.color, width=3))

        # labels
        for tx, ty, tstr, tcol in self.annotations:

            # change the alpha value according to whether this is the selected
            # cell or another part of the tree
            tcol[3] = 255 if tstr == str(self.track_id) else 64

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

        self.plot_view.autoRange()
