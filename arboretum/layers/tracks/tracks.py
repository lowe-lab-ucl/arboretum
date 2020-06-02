from napari.layers.base.base import Layer
from napari.utils.event import Event

from typing import Union, Dict, Tuple, List

import numpy as np

from scipy.spatial import cKDTree

class Tracks(Layer):
    """ Tracks

    A napari-style Tracks layer for overlaying trajectories on image data.

    data is of the format:
        t,x,y,(z),....,n

    metadata is a list of metadata associated with tracks. this can include
    information about branching in trees, states and so on:

        [{'id':0, 'b':0, 'e':100', 'p':[0], 'r': 0, 'states':[]}, ...]

    importantly, p (parent) is a list of track IDs that are parents of the
    track, this can be one (the track has one parent, and the parent has >=1
    child) or more than one (the track has multiple parents, but only one child)

    Data format:
        data: a list of np.ndarrays
        metadata: associated track metadata and adjacency graph

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
        edge_width=2,
        tail_length=30,
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
    ):

        # if not provided with any data, set up an empty layer in 2D+t
        if data is None:
            data = [np.empty((0, 3))]

        ndim = self._check_track_dimensionality(data)

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

        # use a kdtree to help with fast lookup of the nearest track
        self._kdtree = None

        # track manager
        self.manager = manager

        # NOTE(arl): _tracks and _connex store raw data for vispy
        self._tracks = None
        self._connex = None
        self.data = data

        if manager is not None:
            self.data = manager.data_experimental


        self.edge_width = edge_width
        self.tail_length = tail_length
        self.display_id = False
        self.color_by = 0



        self._update_dims()


    def _get_extent(self) -> List[Tuple[int, int, int]]:
        """Determine ranges for slicing given by (min, max, step)."""
        print('called')
        minmax = lambda x: (int(np.min(x)), int(np.max(x)), 1)
        return [minmax(self._tracks[:,i]) for i in range(self.ndim)]

    def _get_ndim(self) -> int:
        """Determine number of dimensions of the layer."""
        return self._tracks.shape[1]

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
        """ use a kd-tree to lookup the ID of the nearest tree """
        if self._kdtree is None:
            return

        coords = np.array([self.coordinates[c] for c in (0, 2, 1)])
        d, idx = self._kdtree.query(coords, k=10)
        pruned = [i for i in idx if self._tracks[i,0]==coords[0]]
        if pruned:
            return self.manager._meta[pruned[0], 0] # return the track ID


    def _update_thumbnail(self):
        """Update thumbnail with current points and colors."""
        pass

    def _view_data(self):
        """ return a view of the data """
        return self._tracks[:, self.dims.displayed]


    @property
    def current_frame(self):
        return self.dims.indices[0]


    @property
    def data(self) -> list:
        """list of (N, D) arrays: coordinates for N points in D dimensions."""
        return self._data

    @data.setter
    def data(self, data: list):
        self._data = data

        # build the connex for the data
        cnx = lambda d: [True]*(d.shape[0]-1) + [False]

        # build the track data for vispy
        self._tracks = np.concatenate(self.data, axis=0)
        self._connex = np.concatenate([cnx(d) for d in data], axis=0)

        # build a tree of the track data to allow fast lookup of nearest track
        self._kdtree = cKDTree(self._tracks)



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


    def _check_track_dimensionality(self, data: list):
        """ check the dimensionality of the data

        TODO(arl): we could allow a mix of 2D/3D etc...
        """
        assert(all([isinstance(d, np.ndarray) for d in data]))
        assert(all([d.shape[1] == data[0].shape[1] for d in data]))
        return data[0].shape[1]

    @property
    def vertex_connex(self) -> np.ndarray:
        # return self.manager.track_connex
        return self._connex

    @property
    def vertex_colors(self) -> np.ndarray:
        return self.manager.track_colors

    @property
    def vertex_times(self) -> np.ndarray:
        return self._tracks[:,0]
