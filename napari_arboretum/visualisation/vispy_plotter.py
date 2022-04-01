import numpy as np
from qtpy.QtWidgets import QWidget
from vispy import scene

from ..tree import Annotation, Edge
from .base_plotter import TreePlotterQWidgetBase

__all__ = ["VisPyPlotter"]


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

    def autoscale_view(self) -> None:
        """Scale the canvas so all branches are in view."""
        xs = np.concatenate([track.pos[:, 0] for id, track in self.tree.tracks.items()])
        ys = np.concatenate([track.pos[:, 1] for id, track in self.tree.tracks.items()])
        rect = np.min(xs), np.min(ys), np.ptp(xs), np.ptp(ys)
        self.view.camera.rect = rect

    def update_colors(self) -> None:
        """
        Update plotted track colors from the colors in self.edges.
        """
        for e in self.edges:
            if e.id is not None:
                self.tree.tracks[e.id].set_data(color=e.color)

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

    def set_title(self, title: str) -> None:
        """
        Set the title of the plot.
        """
        pass


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

    def add_track(self, id: int, pos: np.ndarray, color: np.ndarray) -> None:
        """
        Parameters
        ----------
        pos :
            Array of shape (n, 2) specifying vertex coordinates.
        color :
            Array of shape (n, 4) specifying RGBA values in range [0, 1].
        """
        visual = scene.visuals.Line(pos=pos, color=color, width=3)
        scene.visuals.Compound.add_subvisual(self, visual)
        self.tracks[id] = visual
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
