from dataclasses import dataclass
from typing import Optional

import numpy as np
from qtpy.QtWidgets import QWidget
from vispy import scene

from ..tree import Annotation, Edge
from .base_plotter import TreePlotterQWidgetBase

__all__ = ["VisPyPlotter"]


@dataclass
class Bounds:
    xmin: float
    xmax: float
    ymin: float
    ymax: float


class VisPyPlotter(TreePlotterQWidgetBase):
    """
    Tree plotter using pyqtgraph as the plotting backend.

    Attributes
    ----------
    canvas : vispy.scene.SceneCanvas
        Main plotting canvas
    tree : TreeVisual
        The tree.
    """

    def __init__(self):
        """
        Setup the plot canvas..
        """
        self.canvas = scene.SceneCanvas(keys=None, size=(300, 1200))
        self.view = self.canvas.central_widget.add_view()
        self.view.camera = scene.PanZoomCamera()
        self.tree = TreeVisual(parent=None)
        self.view.add(self.tree)

    def get_qwidget(self) -> QWidget:
        return self.canvas.native

    def clear(self) -> None:
        self.tree.clear()

    @property
    def bounds(self) -> Bounds:
        """
        Return (xmin, ymin, xmax, ymax) bounds of the drawn tree. This does
        not include any annoatations.
        """
        xs = np.concatenate([track.pos[:, 0] for id, track in self.tree.tracks.items()])
        ys = np.concatenate([track.pos[:, 1] for id, track in self.tree.tracks.items()])
        return Bounds(
            xmin=np.min(xs), ymin=np.min(ys), xmax=np.max(xs), ymax=np.max(ys)
        )

    def autoscale_view(self) -> None:
        """Scale the canvas so all branches are in view."""
        xs = np.concatenate([track.pos[:, 0] for id, track in self.tree.tracks.items()])
        ys = np.concatenate([track.pos[:, 1] for id, track in self.tree.tracks.items()])
        padding = 0.1
        width, height = np.ptp(xs), np.ptp(ys)
        rect = (
            np.min(xs) - padding * width,
            np.min(ys) - padding * height,
            width * (1 + 2 * padding),
            height * (1 + 2 * padding),
        )
        self.view.camera.rect = rect

    def update_colors(self) -> None:
        """
        Update plotted track colors from the colors in self.edges.
        """
        for e in self.edges:
            if e.id is not None:
                self.tree.set_branch_color(e.id, e.color)

    def add_branch(self, e: Edge) -> None:
        """
        Add a single branch to the tree.
        """
        self.tree.add_track(e.id, np.column_stack((e.y, e.x)), e.color)
        self.autoscale_view()

    def add_annotation(self, a: Annotation) -> None:
        """
        Add a single label to the tree.
        """
        self.tree.add_annotation(a.x, a.y, a.label, a.color)

    def draw_current_time_line(self, time: int) -> None:
        if not hasattr(self, "_time_line"):
            self._time_line = scene.visuals.Line()
            self.view.add(self._time_line)
        bounds = self.bounds
        padding = (bounds.xmax - bounds.xmin) * 0.1
        self._time_line.set_data(
            pos=np.array([[bounds.xmin - padding, time], [bounds.xmax + padding, time]])
        )


class TreeVisual(scene.visuals.Compound):
    """
    Tree visual that stores branches as sub-visuals.
    """

    def __init__(self, parent):
        super().__init__([])
        self.parent = parent
        self.unfreeze()
        # Keep a reference to tracks we add so their colour can be changed later
        self.tracks = {}
        self.subvisuals = []

    def get_branch_color(self, branch_id: int) -> np.ndarray:
        return self.tracks[branch_id].color

    def set_branch_color(self, branch_id: int, color: np.ndarray) -> None:
        """
        Set the color of an individual branch.
        """
        self.tracks[branch_id].set_data(color=color)

    def add_track(self, id: Optional[int], pos: np.ndarray, color: np.ndarray) -> None:
        """
        Parameters
        ----------
        id :
            Track ID.
        pos :
            Array of shape (2, 2) specifying vertex coordinates.
        color :
            Array of shape (n, 4) specifying RGBA values in range [0, 1] along
            the track.
        """
        if id is None:
            visual = scene.visuals.Line(pos=pos, color=color, width=3)
        else:
            # Split up line into individual time steps so color can vary
            # along the line
            ys = np.arange(pos[0, 1], pos[1, 1] + 1)
            xs = np.ones(ys.size) * pos[0, 0]
            visual = scene.visuals.Line(
                pos=np.column_stack((xs, ys)), color=color, width=3
            )
            self.tracks[id] = visual

        self.add_subvisual(visual)
        self.subvisuals.append(visual)

    def add_annotation(self, x: float, y: float, label: str, color):
        visual = scene.visuals.Text(
            text=label,
            color=color,
            pos=[y, x, 0],
            anchor_x="left",
            anchor_y="top",
            font_size=10,
        )
        self.add_subvisual(visual)
        self.subvisuals.append(visual)

    def clear(self) -> None:
        """Remove all tracks."""
        while self.subvisuals:
            subvisual = self.subvisuals.pop()
            self.remove_subvisual(subvisual)
