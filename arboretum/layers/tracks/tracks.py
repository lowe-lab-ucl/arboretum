from napari.layers.base.base import Layer
from napari.utils.event import Event
from napari.utils.colormaps import colormaps

from typing import Union, Dict, Tuple, List

import numpy as np

from scipy.spatial import cKDTree

from matplotlib.cm import get_cmap

class Tracks(Layer):
    """ Tracks

    A napari-style Tracks layer for overlaying trajectories on image data.


    Parameters
    ----------

        data : list
            list of (NxD) arrays of the format: t,x,y,(z),....,n

        properties : list
            list of dictionaries of track properties:

            [{'ID': 0,
              'parent': [],
              'root': 0,
              'states': [], ...}, ...]

    importantly, p (parent) is a list of track IDs that are parents of the
    track, this can be one (the track has one parent, and the parent has >=1
    child) in the case of splitting, or more than one (the track has multiple
    parents, but only one child) in the case of track merging

    """
    # The max number of points that will ever be used to render the thumbnail
    # If more points are present then they are randomly subsampled
    _max_tracks_thumbnail = 1024

    def __init__(
        self,
        data=None,
        *,
        properties=None,
        graph=None,
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
            properties=Event,
        )

        # use a kdtree to help with fast lookup of the nearest track
        self._kdtree = None

        # NOTE(arl): _tracks and _connex store raw data for vispy
        self._tracks = None
        self._connex = None
        self._points = None
        self._points_id = None
        self._points_lookup = None
        self._ordered_points_idx = None

        self.data = data
        self.properties = properties or []

        self.edge_width = edge_width
        self.tail_length = tail_length
        self.display_id = False
        self.color_by = 'ID' # default color by ID

        self._update_dims()


    def _get_extent(self) -> List[Tuple[int, int, int]]:
        """Determine ranges for slicing given by (min, max, step)."""
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
        pruned = [i for i in idx if self._points[i,0]==coords[0]]
        if pruned and self._points_id is not None:
            return self._points_id[pruned[0]] # return the track ID


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
        """ set the data and build the vispy arrays for display """
        self._data = data

        # build the connex for the data
        cnx = lambda d: [True]*(d.shape[0]-1) + [False]

        # build the track data for vispy
        self._tracks = np.concatenate(self.data, axis=0)
        self._connex = np.concatenate([cnx(d) for d in data], axis=0)

        # build the indices for sorting points by time
        self._ordered_points_idx = np.argsort(self._tracks[:,0])
        self._points = self._tracks[self._ordered_points_idx]

        # build a tree of the track data to allow fast lookup of nearest track
        self._kdtree = cKDTree(self._points)

        # make the lookup
        frames = list(set(self._points[:,0].astype(np.uint).tolist()))
        self._points_lookup = [None] * (max(frames)+1)
        for f in range(max(frames)+1):
            # if we have some data for this frame, calculate the slice required
            if f in frames:
                idx = np.where(self._points[:,0] == f)[0]
                self._points_lookup[f] = slice(min(idx), max(idx)+1, 1)

    @property
    def properties(self) -> list:
        """ return the list of track properties """
        return self._properties

    @properties.setter
    def properties(self, properties: list):
        """ set track properties """
        assert(not properties or len(properties) == len(self.data))

        points_id = []

        # do some type checking/enforcing
        for idx, track in enumerate(properties):
            for key, value in track.items():

                if isinstance(value, np.generic):
                    track[key] = value.tolist()

            # if there is not a track ID listed, generate one on the fly
            if 'ID' not in track:
                track['ID'] = idx

            points_id += [track['ID']] * len(self.data[idx]) # get the length of the track

        self._properties = properties
        self._points_id = np.array(points_id)[self._ordered_points_idx]

        #TODO(arl): not all tracks are guaranteed to have the same keys
        self._property_keys = list(properties[0].keys())

        # properties have been updated, we need to alert the gui
        self.events.properties()


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
    def color_by(self) -> str:
        return self._color_by

    @color_by.setter
    def color_by(self, color_by: str):
        self._color_by = color_by
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
        return self._connex

    @property
    def vertex_colors(self) -> np.ndarray:
        """ return the vertex colors according to the currently selected
        property """

        # TODO(arl): move some of this type checking to the properties setter
        vertex_properties = []
        for idx, track_property in enumerate(self.properties):
            property = track_property[self.color_by]

            if isinstance(property, (list, np.ndarray)):
                p = property
            elif isinstance(property, (int, float, np.generic)):
                p = [property] * len(self.data[idx]) # make it the length of the track
            else:
                raise TypeError('Property {track_property} type not recognized')

            vertex_properties.append(p)

        # concatenate them, and use a colormap to color them
        vertex_properties = np.concatenate(vertex_properties, axis=0)

        colormap = get_cmap('gist_rainbow')
        return colormap(np.mod(vertex_properties, 32)*8)

    @property
    def vertex_times(self) -> np.ndarray:
        return self._tracks[:,0]

    @property
    def track_labels(self):
        """ return track labels """
        # this is the slice into the time ordered points array
        lookup = self._points_lookup[self.current_frame]

        # TODO(arl): this breaks when changing dimensions
        pos = self._points[lookup, self.dims.displayed]
        lbl = [f'ID:{i}' for i in self._points_id[lookup]]
        return zip(lbl, pos)
