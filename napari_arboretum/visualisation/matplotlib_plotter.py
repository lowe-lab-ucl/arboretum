from typing import Optional

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
        self.mpl_time_line: Optional[Line2D] = None

    def get_qwidget(self) -> QWidget:
        return self.mpl_widget

    def plot(self, x: np.ndarray, y: np.ndarray) -> None:
        self.axes.plot(x, y, label=f"id={self.track_id}")

    def draw_current_time_line(self, time: int) -> None:
        if self.mpl_time_line is None:
            self.mpl_time_line = self.axes.axvline(time, color="white")
        else:
            self.mpl_time_line.set_xdata([time])
        self.redraw()

    def set_xlabel(self, label: str) -> None:
        self.axes.set_xlabel(label)

    def set_ylabel(self, label: str) -> None:
        self.axes.set_ylabel(label)

    def set_title(self, title: str) -> None:
        self.axes.set_title(title)

    def clear(self) -> None:
        self.axes.cla()
        self.mpl_time_line = None

    def redraw(self) -> None:
        self.mpl_widget.canvas.draw()
