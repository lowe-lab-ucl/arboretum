import urllib.request
import json

import btrack
import arboretum
import napari

import numpy as np

# REPO_BASE = 'https://raw.githubusercontent.com/quantumjot/BayesianTracker/master'
#
# # get some object data to track
# f = urllib.request.urlopen(f'{REPO_BASE}/examples/objects.json')
# data = json.load(f)
#
# # get a config file
# f = urllib.request.urlopen(f'{REPO_BASE}/models/cell_config.json')
# cfg = json.load(f)
#
#
# # generate some objects to track with using the data
# factory = btrack.dataio._PyTrackObjectFactory()
# objects = []
# for ID, _obj in data.items():
#     txyz = np.array([_obj[k] for k in ['t','x','y','z']])
#     obj = factory.get(txyz, label=int(_obj['label']))
#     objects.append(obj)
#
# # build the config
# cfg = cfg["TrackerConfig"]
# config = {"MotionModel": btrack.utils.read_motion_model(cfg),
#           "ObjectModel": btrack.utils.read_object_model(cfg),
#           "HypothesisModel": btrack.optimise.hypothesis.read_hypothesis_model(cfg)}


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
