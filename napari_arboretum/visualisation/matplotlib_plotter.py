import numpy as np
from matplotlib.lines import Line2D
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

    def draw_current_time_line(self, time: int) -> None:
        if not hasattr(self, "_mpl_time_line"):
            self._mpl_time_line: Line2D = self.axes.axvline(time, color="white")
        else:
            # TODO: fix this
            print(time)
            self._mpl_time_line.set_xdata([time])
        self.mpl_widget.canvas.draw()

    def set_xlabel(self, label: str) -> None:
        self.axes.set_xlabel(label)

    def set_ylabel(self, label: str) -> None:
        self.axes.set_ylabel(label)

    def set_title(self, title: str) -> None:
        self.axes.set_title(title)

    def redraw(self) -> None:
        self.mpl_widget.canvas.draw()
