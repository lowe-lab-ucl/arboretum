# import urllib.request
# import json

import btrack
import arboretum
import napari

import numpy as np


objects = btrack.utils.import_JSON('./objects.json')
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


with napari.gui_qt():
    viewer = napari.Viewer()
    arboretum.build_plugin(viewer, tracks)
