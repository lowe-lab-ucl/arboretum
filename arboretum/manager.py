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



class TrackManager:
    """ TrackManager

    Deals with the track data and appropriate slicing for display

    """
    def __init__(self, tracks):
        self.tracks = tracks

        # build trees from the tracks
        self._trees = btrack.utils.build_trees(tracks)

    @property
    def trees(self): return self._trees

    @property
    def data(self):
        return [np.stack([t.t, t.y, t.x], axis=-1) for t in self.tracks]

    @property
    def properties(self):
        return [{'ID': t.ID, 'root': t.root, 'parent': t.parent, 'states':t.state} for t in self.tracks]
