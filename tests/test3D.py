# import urllib.request
# import json

import btrack
import napari

import numpy as np


def mercator(data):
    """ mercator projection """
    R = 160.
    S = 100.

    data[:, 4] = data[:, 4] - 600.
    data[:, 3] = data[:, 3] - 800.
    t = data[:, 1]

    longitude = data[:, 4] / R
    latitude = 2. * np.arctan(np.exp(data[:, 3]/R)) - np.pi/2

    data[:, 4] = S * np.cos(latitude) * np.cos(longitude)
    data[:, 3] = S * np.cos(latitude) * np.sin(longitude)
    data[:, 2] = S * np.sin(latitude)

    return data

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

    # get the tracks, properties and graph
    data, properties, graph = tracker.to_napari(ndim=3)
    data = mercator(data)

with napari.gui_qt():
    viewer = napari.Viewer()
    viewer.add_tracks(data, properties=properties, graph=graph, name='tracks')
