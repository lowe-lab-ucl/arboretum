import numpy as np
from napari_matplotlib.base import NapariMPLWidget
from qtpy.QtWidgets import QWidget

from .base_plotter import PropertyPlotterBase


class MPLPropertyPlotter(PropertyPlotterBase):
    def __init__(self, viewer):
        self.mpl_widget = NapariMPLWidget(viewer)
        self.figure = self.mpl_widget.canvas.figure
        self.axes = self.mpl_widget.canvas.figure.add_subplot(111)

    def get_qwidget(self) -> QWidget:
        return self.mpl_widget

    def plot(self, x: np.ndarray, y: np.ndarray) -> None:
        self.axes.cla()
        self.axes.plot(x, y, label=f"id={self.track_id}")
        self.mpl_widget.canvas.draw()

    def set_xlabel(self, label: str) -> None:
        self.axes.set_xlabel(label)
        self.mpl_widget.canvas.draw()

    def set_ylabel(self, label: str) -> None:
        self.axes.set_ylabel(label)
        self.mpl_widget.canvas.draw()

    def draw_track_id(self, title: int) -> None:
        self.axes.legend()
        self.mpl_widget.canvas.draw()
