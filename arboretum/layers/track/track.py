from napari.layers.base.base import Layer
from napari.utils.event import Event

from typing import Union, Dict, Tuple, List

import numpy as np

class Tracks(Layer):
    """ Tracks

    A napari-style Tracks layer for overlaying trajectories on image data.

    data is of the format:
        t,x,y,(z)

    nodes is of the format:
        l,b,e,p,(r)

    Data format:
        data: a list of np.ndarrays
        nodes: a list of nodes, organized as an LBEP table

    Notes:
        - Does not currently accept 'data', but builds the data from a track
          manager instance. For integration into napari, should we build  the
          track manager from the array of data?

    """
    # The max number of points that will ever be used to render the thumbnail
    # If more points are present then they are randomly subsampled
    _max_tracks_thumbnail = 1024

    def __init__(
        self,
        data=None,
        *,
        properties=None,
        size=10,
        edge_width=2,
        tail_length=30,
        edge_color=np.array((1.,1.,1.)),
        edge_colormap='viridis',
        color_by=0,
        n_dimensional=True,
        name=None,
        metadata=None,
        scale=None,
        translate=None,
        opacity=1,
        blending='translucent',
        visible=True,
        manager=None,
        nodes=None,
    ):

        if data is None:
            data = np.empty((0, 3))
        else:
            data = np.atleast_3d(data)
        ndim = data.shape[1]

        super().__init__(
            data,
            ndim,
            name=name,
            metadata=metadata,
            scale=scale,
            translate=translate,
            opacity=opacity,
            blending=blending,
            visible=visible,
        )

        self.events.add(
            edge_width=Event,
            edge_color=Event,
            tail_length=Event,
            display_id=Event,
            current_edge_color=Event,
            current_properties=Event,
            n_dimensional=Event,
            color_by=Event,
        )

        # track manager
        self.manager = manager

        self.current_frame = 0
        self.colormap = edge_colormap
        self.edge_width = edge_width
        self.tail_length = tail_length
        self.display_id = False
        self.color_by = 0

        self._update_dims()

        # set data for the current view/dims
        self._view_data()

        self.dims.events.axis.connect(self._update_displayed)

    def _update_displayed(self, event):
        """ update the display frame """
        if event.axis == 0:
            self.current_frame = self.dims.indices[0]

    def _get_extent(self) -> List[Tuple[int, int, int]]:
        """Determine ranges for slicing given by (min, max, step)."""
        return self.manager.extent

    def _get_ndim(self) -> int:
        """Determine number of dimensions of the layer."""
        return self.manager.ndim

    def _get_state(self):
        """Get dictionary of layer state.

        Returns
        -------
        state : dict
            Dictionary of layer state.
        """
        state = self._get_base_state()
        state.update(
            {
                'edge_width': self.edge_width,
                'tail_length': self.tail_length,
                'properties': self.properties,
                'n_dimensional': self.n_dimensional,
                'size': self.size,
                'data': self.data,
            }
        )
        return state

    def _set_view_slice(self):
        """Sets the view given the indices to slice with."""
        return

    def _get_value(self):
        return

    def _update_thumbnail(self):
        """Update thumbnail with current points and colors."""
        pass

    def _view_data(self):
        data = self.manager.data[:, self.dims.displayed]
        self.data = data


    @property
    def data(self) -> np.ndarray:
        """(N, D) array: coordinates for N points in D dimensions."""
        return self._data

    @data.setter
    def data(self, data: np.ndarray):
        self._data = data


    @property
    def edge_color(self) -> np.ndarray:
        """(1 x 4) np.ndarray: Array of RGBA edge colors (applied to all vectors)"""
        return self._edge_color

    @property
    def edge_width(self) -> Union[int, float]:
        """float: Width for all vectors in pixels."""
        return self._edge_width

    @edge_width.setter
    def edge_width(self, edge_width: Union[int, float]):
        self._edge_width = edge_width
        self.events.edge_width()
        self.refresh()
        # self.status = format_float(self.edge_width)

    @property
    def tail_length(self) -> Union[int, float]:
        """float: Width for all vectors in pixels."""
        return self._tail_length

    @tail_length.setter
    def tail_length(self, tail_length: Union[int, float]):
        self._tail_length = tail_length
        self.manager.tail_length = tail_length
        self.events.tail_length()
        self.refresh()
        # self.status = format_float(self.edge_width)

    @property
    def display_id(self) -> bool:
        return self._display_id

    @display_id.setter
    def display_id(self, value: bool):
        self._display_id = value
        self.events.display_id()
        self.refresh()

    @property
    def color_by(self) -> int:
        return self.manager.color_by

    @color_by.setter
    def color_by(self, color_by: int):
        self.manager.color_by = color_by
        self.events.color_by()
        self.refresh()
