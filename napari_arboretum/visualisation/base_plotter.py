from __future__ import annotations

import abc

import numpy as np
import pandas as pd
from qtpy.QtWidgets import QWidget

from napari_arboretum.graph import TreeNode, build_subgraph
from napari_arboretum.tree import Annotation, Edge, layout_tree
from napari_arboretum.util import TrackPropertyMixin

GUI_MAXIMUM_WIDTH = 600

__all__ = ["TreePlotterBase", "TreePlotterQWidgetBase"]


class TreePlotterBase(abc.ABC, TrackPropertyMixin):
    """
    Base class for a `napari.layers.Tracks` plotter.

    This class is designed to handle the translation from a `napari.layers.Tracks`
    layer to visual objects that can be plotted (e.g. lines, text). As such its
    only state is the ``_tracks`` attribute.

    This is not designed to actually render the plotting objects objects.
    Sub-classes should do that by impelmenting the abstract methods defined below.

    Attributes
    ----------
    edges : List[Edge]
    annotations : List[Annotation]
    """

    def on_track_id_change(self) -> None:
        self.draw_tree()

    @property
    def has_tracks(self) -> bool:
        return hasattr(self, "_tracks")

    def draw_tree(self) -> None:
        """
        Plot the tree.
        """
        self.clear()
        subgraph_nodes = build_subgraph(self.tracks, self.track_id)
        self.draw_from_nodes(subgraph_nodes, self.track_id)

    def draw_from_nodes(self, tree_nodes: list[TreeNode], track_id: int | None = None):
        self.edges, self.annotations = layout_tree(tree_nodes)

        if self.has_tracks:
            self.update_edge_colors(update_live=False)

        for e in self.edges:
            self.add_branch(e)

        # labels
        for a in self.annotations:
            self.add_annotation(a)

        self.draw_tree_visual()

    def update_edge_colors(self, *, update_live: bool = True) -> None:
        """
        Update tree edge colours from the track properties.

        Parameters
        ----------
        update_live : bool
            If `True`, also call `update_colors()` on the plotting backend
            to update the colors in a live plot.
        """
        for e in self.edges:
            if e.track_id is not None:
                e.color = self.tracks.track_colors[
                    self.tracks.properties["track_id"] == e.track_id
                ]

        if update_live:
            self.update_colors()

    @abc.abstractmethod
    def update_colors(self) -> None:
        """
        Use the colors stored in self.edges to update the colors in a live
        plot.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def clear(self) -> None:
        """
        Clear the plotting canvas. Called to remove the previous tree when
        a new tree is drawn.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def add_branch(self, e: Edge) -> None:
        """
        Add a single branch to the tree.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def add_annotation(self, a: Annotation) -> None:
        """
        Add a single label to the tree.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def draw_current_time_line(self, time: int) -> None:
        """
        Draw a horizontal line at the current timestep to the tree.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def draw_tree_visual(self) -> None:
        """
        Function to draw the visual after construction.
        """
        raise NotImplementedError


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


class PropertyPlotterBase(abc.ABC, TrackPropertyMixin):
    """
    Base class for plotting a 1D graph of track property against time.
    """

    def on_track_id_change(self) -> None:
        self.plot_property()

    def plot_property(self) -> None:
        """
        Plot a property. The property is taken from the currently selected
        layer, currently selected track_id, and the property used to 'color_by'
        in the napari viewer.
        """
        t, prop = self.get_track_properties()

        self.clear()
        self.plot(t, prop)
        self.set_xlabel("Time")
        self.set_ylabel("Property value")
        self.set_title(f"{self.tracks.color_by}, cell #{self.track_id}")
        self.redraw()

    def get_track_properties(self) -> tuple[np.ndarray, np.ndarray]:
        """
        For a given layer and track_id, get time values and property that
        the track is currently coloured by.

        Returns
        -------
        t :
            Time values.
        prop :
            Property values.
        """
        all_props = pd.DataFrame(self.tracks.properties)
        all_props = all_props.loc[all_props["track_id"] == self.track_id]
        t = self.tracks.data[self.tracks.data[:, 0] == self.track_id, 1]
        return t, all_props[self.tracks.color_by].values

    @abc.abstractmethod
    def get_qwidget(self) -> QWidget:
        """
        Return the native QWidget for embedding.
        """

    @abc.abstractmethod
    def plot(self, x: np.ndarray, y: np.ndarray) -> None:
        """
        Plot x, y values.
        """

    @abc.abstractmethod
    def draw_current_time_line(self, time: int) -> None:
        """
        Indicate the current time (ie. napari viewer z-step) on the plot.
        """

    @abc.abstractmethod
    def set_xlabel(self, label: str) -> None:
        """
        Set x-label.
        """

    @abc.abstractmethod
    def set_ylabel(self, label: str) -> None:
        """
        Set y-label.
        """

    @abc.abstractmethod
    def set_title(self, title: str) -> None:
        """
        Set plot title.
        """

    def clear(self) -> None:
        """
        Optional method that can be implemented by sub-classes to clear
        a figure before updating with new data.
        """

    def redraw(self) -> None:
        """
        Optional method that can be implemented by sub-classes to re-draw
        a figure after the plot and labels have been set.
        """
