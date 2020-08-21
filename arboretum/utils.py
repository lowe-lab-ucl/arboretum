#-------------------------------------------------------------------------------
# Name:     Arboretum
# Purpose:  Dockable widget, and custom track visualization layers for Napari,
#           to cell/object track data.
#
# Authors:  Alan R. Lowe (arl) a.lowe@ucl.ac.uk
#
# License:  See LICENSE.md
#
# Created:  01/05/2020
#-------------------------------------------------------------------------------

import os
import re

import btrack
import multiprocessing

import numpy as np
from scipy.ndimage import measurements


from .io import ArboretumHDFHandler, TrackerFrozenState
from btrack.constants import BayesianUpdates


from functools import wraps
from multiprocessing import Process, SimpleQueue

def process_worker(fn):
    """ Decorator to run function as a process """
    @wraps(fn)
    def _process(*args, **kwargs):

        def _worker(*args, **kwargs):
            q = args[0]
            r = fn(*args[1:], **kwargs)
            q.put(r)

        queue = SimpleQueue()
        process = Process(target=_worker, args=(queue, *args), kwargs=kwargs)
        process.start()
        result = queue.get()
        process.join()

        return result

    return _process





class _Stack:
    """ _Stack

    treat an image stack as a python iterator to enable multiprocessing.Pool
    to function on the stack.

    """
    def __init__(self, data):

        # basic assertions on the data
        assert(isinstance(data, np.ndarray))
        # assert(data.dtype == np.uint8)

        self._stack = data
        self._idx = 0

    def __iter__(self): return self
    def __next__(self):
        if self._idx >= self._stack.shape[0]:
            raise StopIteration
        current = self._idx
        self._idx += 1
        return self._stack[current,...], current



def _localize_process(data: tuple,
                      is_binary: bool = True) -> np.ndarray:
    # image: np.ndarray, frame: int) -> np.ndarray:
    """ worker process for localizing and labelling objects

    volumetric data is usually of the format: t, z, x, y

    Returns:
        combined data in form of nx5 array (t, x, y, z, label) adding a
        z-dimension of uniform zero, if one doesn't exist.
    """

    image, frame = data
    assert image.dtype in (np.uint8, np.uint16)

    if is_binary:
        labeled, n = measurements.label(image.astype(np.bool))
        idx = list(range(1, n+1))
    else:
        labeled = image
        idx = [p for p in np.unique(labeled) if p>0]

    # calculate the centroids

    centroids = np.array(measurements.center_of_mass(image,
                                                     labels=labeled,
                                                     index=idx))

    # if we're dealing with volumetric data, reorder so that z is last
    if image.ndim == 3:
        centroids = np.roll(centroids, -1)

    localizations = np.zeros((centroids.shape[0], 5), dtype=np.uint16)
    localizations[:,0] = frame # time
    localizations[:,1:centroids.shape[1]+1] = centroids
    localizations[:,-1] = 0 #labels-1 #-1 because we use a label of zero for states

    return localizations


def _is_binary_segmentation(image):
    """ guess whether this is a binary or unique/integer segmentation based on
    the data in the image. """
    objects = measurements.find_objects(image)
    labeled, n = measurements.label(image.astype(np.bool))
    return n > len(objects)



def localize(stack_as_array: np.ndarray,
             **kwargs):
    """ localize

    get the centroids of all objects given a segmentaion mask from Napari.

    Should work with volumetric data, and infers the object class label from
    the segmentation label.

    Parameters:
        stack_as_array: a numpy array of the stack, typically the data from
            a napari 'labels' layer

    Notes:
        - multiprocessing is not a good options for use with the GUI. Change to
        a generator
    """

    if 'binary_segmentation' not in kwargs:
        is_binary = _is_binary_segmentation(stack_as_array[0,...])
        print(f'guessing is_binary: {is_binary}')
    else:
        is_binary = kwargs['binary_segmentation']
        assert type(is_binary) == type(bool)

    stack = _Stack(stack_as_array)
    localizations=[_localize_process(s, is_binary=is_binary) for s in stack]
    return np.concatenate(localizations, axis=0)





def _get_btrack_cfg(filename=None):
    """ get a config from a local file or request one over the web

    NOTES:
        - appends the filename of the config for display in the gui. not used
        per se by the tracker.

    """

    if filename is not None:
        config = btrack.utils.load_config(filename)
        config['Filename'] = filename
        return config

    raise IOError



def track(localizations: np.ndarray,
          config: dict,
          volume: tuple = ((0,1200),(0,1600),(-1e5,1e5)),
          optimize: bool = True,
          method: BayesianUpdates = BayesianUpdates.EXACT,
          search_radius: int = None,
          min_track_len: int = 2):

    """ track

    Run BayesianTracker with the localizations from the localize function

    """

    n_localizations = localizations.shape[0]
    idx = range(n_localizations)

    # convert the localizations into btrack objects
    from btrack.dataio import  _PyTrackObjectFactory
    factory = _PyTrackObjectFactory()
    objects = [factory.get(localizations[i,:4], label=int(localizations[i,-1])) for i in idx]

    # for obj in objects:
    #     obj.z = obj.z * 10.

    # initialise a tracker session using a context manager
    with btrack.BayesianTracker() as tracker:

        # configure the tracker using a config file, append objects and set vol
        tracker.configure(config)
        tracker.append(objects)

        tracker.volume = volume
        tracker.update_method = method

        if search_radius is not None:
            tracker.max_search_radius = search_radius

        # track them and (optionally) optimize
        tracker.track_interactive(step_size=100)

        if optimize:
            tracker.optimize(options={'tm_lim': int(6e4)})

        # dump all of the data into the frozen state
        frozen_tracker = TrackerFrozenState()
        frozen_tracker.set(tracker)

        frozen_tracker.tracks = [t for t in frozen_tracker.tracks if len(t)>=min_track_len]

    # for track in frozen_tracker.tracks:
    #     for obj in track._data:
    #         obj.z = obj.z / 10.

    return frozen_tracker



def _color_segmentation_by_state(h, color_segmentation=False):
    # TODO(arl): implement this!
    # if not color_segmentation:
    return h.segmentation





def load_hdf(filename: str,
             filter_by: str = 'area>=100',
             load_segmentation: bool = True,
             load_objects: bool = True,
             color_segmentation: bool = True):

    """ load data from an HDF file """
    with ArboretumHDFHandler(filename) as h:
        h._f_expr = filter_by

        if 'segmentation' in h._hdf and load_segmentation:
            seg = _color_segmentation_by_state(h, color_segmentation)
            seg = seg.astype(np.uint8)
        else:
            seg = None

        # get the objects and strip out the data
        if 'objects' in h._hdf and load_objects:
            obj = h.filtered_objects(f_expr=filter_by)
            loc = np.stack([[o.t, o.x, o.y, o.z, o.label] for o in obj], axis=0)
            loc = loc.astype(np.uint16)
        else:
            loc = np.empty((0,3))

        # get the tracks
        if 'tracks' in h._hdf:
            tracks = h.tracks
        else:
            tracks = []

        # correct files originating from earlier versions of the tracker
        for trk_set in tracks:
            for trk in trk_set:
                if trk.is_root and trk.root == 0:
                    trk.root = trk.ID

    return seg, loc, tracks


def load_json(filename: str):
    """ load json data """
    filepath, fn = os.path.split(filename)

    pattern = 'tracks_(\w+).json'
    match = re.match(pattern, fn)
    if match:
        cell_type = match.group(1)
    else:
        cell_type = 'None'

    tracks = btrack.dataio.import_all_tracks_JSON(filepath, cell_type=cell_type)
    return tracks



def export_hdf(filename: str,
               segmentation: np.ndarray = None,
               tracker_state: TrackerFrozenState = None):
    """ export the tracking data to an hdf file """

    if os.path.exists(filename):
        raise IOError(f'{filename} already exists!')

    with ArboretumHDFHandler(filename, 'w') as h:
        h.write_segmentation(segmentation)

        if tracker_state is not None:
            if tracker_state.objects is not None:
                h.write_objects(tracker_state, obj_type='obj_type_1')
            if tracker_state.tracks is not None:
                h.write_tracks(tracker_state, obj_type='obj_type_1')


if __name__ == '__main__':
    pass
