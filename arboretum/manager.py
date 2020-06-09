

import numpy as np

from .lineage import generation


def displacement(track):
    """ hacky displacement calculation """
    displacements = [0.]
    for i in range(1,len(track)):
        d = np.sqrt((track.x[i]-track.x[i-1])**2 + (track.y[i]-track.y[i-1])**2 + (track.z[i]-track.z[i-1])**2)
        displacements.append(d)
    return displacements


def survivor(tracks, track):
    """ eye of the tiger """
    root = [t for t in tracks if t.ID == track.root]
    if root:
        return 1 if root[0].t[0] <= 30 else 0
    return 0







def planar(track):
    return np.stack([track.t, track.x, track.y], axis=-1)

def volumetric(track):
    return np.stack([track.t, track.x, track.y, track.z], axis=-1)

def mercator(track):
    """ mercator projection """
    R = 160.
    S = 100.

    x0 = np.array(track.x) - 600.
    y0 = np.array(track.y) - 800.
    t = np.array(track.t)

    longitude = x0 / R
    latitude = 2. * np.arctan(np.exp(y0/R)) - np.pi/2

    x = S * np.cos(latitude) * np.cos(longitude)
    y = S * np.cos(latitude) * np.sin(longitude)
    z = S * np.sin(latitude)

    return np.stack([t, x, y, z], axis=-1)


class TrackManager:
    """ TrackManager

    Deals with the track data and appropriate slicing for display

    """
    def __init__(self,
                 tracks,
                 transform=planar):


        self.tracks = tracks
        self.transform = transform

        # build trees from the tracks
        # self._trees = build_trees(self.tracks)

    @property
    def trees(self): return self._trees

    @property
    def data(self):
        """ should be ordered t, z, y, x for 3D """
        return [self.transform(t) for t in self.tracks]

    @property
    def properties(self):
        return [{'ID': t.ID,
                 'root': t.root,
                 'parent': t.parent,
                 'time': t.t,
                 'states': t.state,
                 'fate': t.fate.value,
                 'survivor': survivor(self.tracks, t),
                 'generation': t.generation} for t in self.tracks]
