from typing import Sequence

import pyqtgraph as pg
from qtpy.QtWidgets import QWidget

from .base_plotter import TreePlotterQWidgetBase

__all__ = ["PyQtGraphPlotter"]


class PyQtGraphPlotter(TreePlotterQWidgetBase):
    """
    Tree plotter using pyqtgraph as the plotting backend.

    Attributes
    ----------
    plot_widget : pyqtgraph.GraphicsLayoutWidget
        Main plotting widget.
    """

    def __init__(self):
        """
        Setup the plot view.
        """
        self.plot_widget = pg.GraphicsLayoutWidget()
        self.plot_view = self.plot_widget.addPlot(
            title="Lineage tree", labels={"left": "Time"}
        )
        self.plot_view.hideAxis("bottom")

    def get_qwidget(self) -> QWidget:
        return self.plot_widget

    def add_branch(self, x: Sequence[float], y: Sequence[float], color) -> None:
        """
        Add a single branch to the tree.
        """
        # napari uses [0, 1] RGBA, pygraphqt uses [0, 255] RGBA
        color = color * 255
        self.plot_view.plot(y, x, pen=pg.mkPen(color=color, width=3))

    def add_annotation(self, x: float, y: float, label: str, color) -> None:
        """
        Add a single label to the tree.
        """
        # napari uses [0, 1] RGBA, pygraphqt uses [0, 255] RGBA
        color = color * 255
        pt = pg.TextItem(
            text=label,
            color=color,
            html=None,
            anchor=(0, 0),
            border=None,
            fill=None,
            angle=0,
            rotateAxis=None,
        )
        pt.setPos(y, x)
        self.plot_view.addItem(pt, ignoreBounds=True)

    def set_title(self, title: str) -> None:
        """
        Set the title of the plot.
        """
        self.plot_view.setTitle(title)

    def draw_tree(self, track_id: int) -> None:
        """
        Plot graph on the plugin canvas.
        """
        self.plot_view.clear()
        # NOTE(arl): disabling the autoranging improves perfomance dramatically
        # https://stackoverflow.com/questions/17103698/plotting-large-arrays-in-pyqtgraph
        self.plot_view.disableAutoRange()
        super().draw_tree(track_id)
        self.plot_view.autoRange()
