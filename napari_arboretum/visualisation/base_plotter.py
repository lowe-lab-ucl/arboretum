import abc
from typing import Sequence

import napari
import numpy as np
from qtpy.QtWidgets import QWidget

from ..graph import build_subgraph, layout_subgraph
from ..tree import ColorType

GUI_MAXIMUM_WIDTH = 600

__all__ = ["TreePlotterBase", "TreePlotterQWidgetBase"]


class TreePlotterBase(abc.ABC):
    """
    Base class for a `napari.layers.Tracks` plotter.

    This class is designed to handle the translation from a `napari.layers.Tracks`
    layer to visual objects that can be plotted (e.g. lines, text). As such its
    only state is the ``_tracks`` attribute.

    This is not designed to actually render the plotting objects objects.
    Sub-classes should do that by impelmenting the abstract methods defined below.
    """

    @property
    def tracks(self) -> napari.layers.Tracks:
        """
        The napari tracks layer associated with this plotter.
        """
        if not hasattr(self, "_tracks"):
            raise AttributeError("No tracks set on this plotter.")
        return self._tracks

    @tracks.setter
    def tracks(self, track_layer: napari.layers.Tracks):
        self._tracks = track_layer

    def draw_tree(self, track_id: int) -> None:
        """
        Plot the tree containing ``track_id``.
        """
        root, subgraph_nodes = build_subgraph(self.tracks, track_id)
        self.edges, self.annotations = layout_subgraph(root, subgraph_nodes)

        self.set_title(f"Lineage tree: {track_id}")

        self.plot_branches()

        # labels
        for a in self.annotations:
            # change the alpha value according to whether this is the selected
            # cell or another part of the tree
            color = a.color
            color[3] = 1 if a.label == str(track_id) else 0.25
            self.add_annotation(a.x, a.y, a.label, a.color)

    def plot_branches(self) -> None:
        """
        Plot the branches.

        This is separated from `draw_tree` so it can be used in callbacks when
        the track colours are changed, but the track_id is not.
        """
        for e in self.edges:
            if e.id is not None:
                color = self.tracks.track_colors[
                    np.where(self.tracks.properties["track_id"] == e.id)
                ]
                # For a track that has colour varying along it, just select the
                # first colour for now
                color = color[-1, :]
            else:
                color = e.color
            self.add_branch(e.x, e.y, color)

    @abc.abstractmethod
    def add_branch(
        self, x: Sequence[float], y: Sequence[float], color: ColorType
    ) -> None:
        """
        Add a single branch to the tree.

        Parameters
        ----------
        x, y : Sequence[float]
            x/y coordinates of the branch.
        color : ColorType
            Color in a RGBA tuple with values in the range [0, 1].
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def add_annotation(self, x: float, y: float, label: str, color: ColorType) -> None:
        """
        Add a single label to the tree.

        Parameters
        ----------
        x, y : float
            x/y coordinate of the annotation.
        label : str
            Annotation text.
        color : ColorType
            Color in a RGBA tuple with values in the range [0, 1].
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def set_title(self, title: str) -> None:
        """
        Set the title of the plot.

        Parameters
        ----------
        title : str
            Plot title.
        """
        raise NotImplementedError()


class TreePlotterQWidgetBase(TreePlotterBase):
    """
    Base class for a tree plotter that provides a QWidget
    (e.g. for embedding in a napari plugin).
    """

    @abc.abstractmethod
    def get_qwidget(self) -> QWidget:
        """
        Return the native QWidget for embedding.
        """
        raise NotImplementedError()
