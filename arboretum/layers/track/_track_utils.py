import btrack

import numpy as np

from matplotlib.cm import get_cmap
from matplotlib.colors import ListedColormap




# state colors are grey, blue, green, magenta, red
STATE_COLORMAP = np.array([[0.5,0.5,0.5,1.0],
                           [0.0,0.0,1.0,1.0],
                           [0.0,1.0,0.0,1.0],
                           [1.0,0.0,1.0,1.0],
                           [1.0,0.0,0.0,1.0]])
state_cmap = ListedColormap(STATE_COLORMAP)


class Track:
    def __init__(self):
        pass


class TrackManager:
    """ TrackManager

    Deals with the track data and appropriate slicing for display

    """
    def __init__(self, tracks):
        self.tracks = tracks
        self._frame_range = (np.min([np.min(t.t) for t in self.tracks]),
                             np.max([np.max(t.t) for t in self.tracks]))


        self._color_by_colormaps = [(get_cmap('prism'), 32, 8),
                                    (get_cmap('prism'), 32, 8),
                                    (get_cmap('prism'), 32, 8),
                                    (state_cmap, 5, 1)]
        self.color_by = 0

        self._data = []
        self._meta = []
        self._connex = []

        # build the frame map
        self._build_track_data()

        # build trees from the tracks
        self._trees = btrack.utils.build_trees(tracks)



    @property
    def color_by(self):
        return self._color_by

    @color_by.setter
    def color_by(self, value):
        self._color_by = value
        cmap, cmod, cmul = self._color_by_colormaps[value]
        self.cmap = lambda x: cmap(np.mod(x, cmod) * cmul)

    @property
    def frame_range(self):
        return self._frame_range

    @property
    def extent(self):
        minmax = lambda x: (int(np.min(x)), int(np.max(x)), 1)
        return [ minmax(self._data[:,i]) for i in range(self.data.shape[-1]) ]

    @property
    def ndim(self):
        return self.data.shape[-1]

    @property
    def trees(self): return self._trees

    @property
    def track_colors(self):
        return self.cmap(self._meta[:, self.color_by])

    @property
    def track_connex(self):
        return self._connex

    def _build_track_data(self):
        """ build a lookup table for tracks that are in a given frame """
        self._frame_map = {i:[] for i in range(self._frame_range[1]+1)}

        for track in self.tracks:
            for frame in track.t:
                self._frame_map[frame].append( track )


        # build the display arrays from the data
        for track in self.tracks:
            # connex allows GL to draw a single line for all tracks, but with
            # splits between tracks
            connex = [True] * len(track)
            connex[-1] = False
            self._connex.append(connex)

            txyz = np.stack([track.t,
                             track.x,
                             track.y,
                             track.z], axis=-1)

            meta = np.stack([[track.ID]*len(track),
                             [track.root]*len(track),
                             [track.parent]*len(track),
                             track.state], axis=-1)

            # position information: txyz
            self._data.append(txyz)

            # metadata: ID, root, parent, state
            self._meta.append(meta)


        self._data = np.concatenate(self._data, axis=0)
        self._meta = np.concatenate(self._meta, axis=0)
        self._connex = np.concatenate(self._connex, axis=0)


    @property
    def data(self):
        """ return t,x,y,(z) data to the layer """
        return self._data[:,(0,2,1)] # only return xy data atm

    @property
    def nodes(self):
        """ make the nodes of the trees """
        lbepr = np.zeros((len(self.tracks), 5), dtype=np.int)
        for i, trk in enumerate(self.tracks):
            lbepr[i,:] = [trk.ID, trk.t[0], trk.t[-1], trk.parent, trk.root]
        return lbepr



    def tracks_in_frame(self, idx):
        """ return the tracks in a certain frame """
        return self._frame_map[idx]

    def object_IDs(self, idx):
        """ object ID used to label tracks """
        return [f'ID:{t.ID}' for t in self.tracks_in_frame(idx)]

    def object_pos(self, idx):
        """ object position in given frame """
        pos = []
        for track in self.tracks_in_frame(idx):
            t = track.t.index(idx)
            pos.append((track.y[t], track.x[t]))
        return pos
