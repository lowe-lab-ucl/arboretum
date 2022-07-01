from dataclasses import dataclass

import numpy as np
from qtpy.QtWidgets import QWidget
from vispy import scene

from ..tree import Annotation, Edge
from .base_plotter import TreePlotterQWidgetBase

__all__ = ["VisPyPlotter"]


DEFAULT_TEXT_SIZE = 8
DEFAULT_BRANCH_WIDTH = 3


@dataclass
class Bounds:
    xmin: float
    xmax: float
    ymin: float
    ymax: float


@dataclass
class TrackSubvisualProxy:
    pos: np.ndarray
    color: np.ndarray = np.array([1.0, 1.0, 1.0, 1.0])

    @property
    def connex(self):
        connex = [True] * (self.pos.shape[0] - 1) + [False]
        return connex

    @property
    def safe_color(self) -> np.ndarray:
        if self.color.ndim != 2:
            safe_color = np.repeat([self.color], self.pos.shape[0], axis=0)
            return safe_color
        return self.color


@dataclass
class AnnotationSubvisualProxy:
    pos: np.ndarray
    text: str
    color: str = "white"


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

        # change the aspect ratio of the camera if we have just a single branch
        # this will centre the camera on the single branch, otherwise, set the
        # aspect ratio to match the data
        if width == 0:
            self.view.camera.aspect = 1.0
        else:
            self.view.camera.aspect = None
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
        # self.tree.add_track(e.id, np.column_stack((e.y, e.x)), e.color)
        self.tree.add_track(e)
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

    def draw_tree_visual(self) -> None:
        """
        Draw the whole tree.
        """
        self.tree.draw_tree()


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
        self.edges = []
        self.annotations = []

        subvisuals = [
            scene.visuals.Line(color="white", width=DEFAULT_BRANCH_WIDTH),
            scene.visuals.Text(
                anchor_x="left",
                anchor_y="top",
                rotation=90,
                font_size=DEFAULT_TEXT_SIZE,
                color="white",
            ),
        ]

        for visual in subvisuals:
            self.add_subvisual(visual)

    def get_branch_color(self, branch_id: int) -> np.ndarray:
        return self.tracks[branch_id].color

    def set_branch_color(self, branch_id: int, color: np.ndarray) -> None:
        """
        Set the color of an individual branch.
        """
        self.tracks[branch_id].color = color
        self._subvisuals[0].set_data(
            color=np.row_stack([e.safe_color for e in self.edges]),
        )

    def add_track(self, e: Edge) -> None:
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
        color = e.color
        pos = np.column_stack((e.y, e.x))

        if e.node is None:
            subvisual_proxy = TrackSubvisualProxy(
                pos=pos,
                color=np.array([1.0, 1.0, 1.0, 1.0]),
            )
        else:
            # Split up line into individual time steps so color can vary
            # along the line
            ys = np.asarray(e.node.t)  # np.arange(pos[0, 1], pos[1, 1] + 1)
            xs = np.ones(ys.size) * pos[0, 0]
            subvisual_proxy = TrackSubvisualProxy(
                pos=np.column_stack((xs, ys)),
                color=color,
            )
            # store a reference to this subvisual proxy
            self.tracks[e.id] = subvisual_proxy

        self.edges.append(subvisual_proxy)

    def add_annotation(self, x: float, y: float, label: str, color):

        subvisual_proxy = AnnotationSubvisualProxy(
            text=label,
            pos=[y, x, 0],
        )

        self.annotations.append(subvisual_proxy)

    def clear(self) -> None:
        """Remove all tracks."""
        self.tracks = {}
        self.edges = []
        self.annotations = []

        for visual in self._subvisuals:
            visual._pos = None

            if hasattr(visual, "_text"):
                visual._text = None

    def draw_tree(self) -> None:
        """Once the data is added, draw the tree."""

        self._subvisuals[0].set_data(
            pos=np.row_stack([e.pos for e in self.edges]),
            color=np.row_stack([e.safe_color for e in self.edges]),
            connect=np.concatenate([e.connex for e in self.edges]),
        )

        # TextVisual does not have a ``set_data`` method
        self._subvisuals[1].pos = np.asarray([a.pos for a in self.annotations])
        self._subvisuals[1].text = [a.text for a in self.annotations]
