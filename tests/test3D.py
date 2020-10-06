# import urllib.request
# import json

import btrack
import arboretum
import napari

import numpy as np


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


objects = btrack.dataio.import_JSON('./objects.json')
config = btrack.utils.load_config('./cell_config.json')

# track the objects
with btrack.BayesianTracker() as tracker:

    # configure the tracker using a config file, append objects and set vol
    tracker.configure(config)
    tracker.append(objects)
    tracker.volume = ((0,1200),(0,1600),(-1e5,1e5))

    # track them and (optionally) optimize
    tracker.track_interactive(step_size=100)
    tracker.optimize()

    # get the tracks as a python list
    tracks = tracker.tracks



manager = arboretum.TrackManager(tracks, transform=mercator)



with napari.gui_qt():
    viewer = napari.Viewer()
    arboretum.build_plugin(viewer, manager)
