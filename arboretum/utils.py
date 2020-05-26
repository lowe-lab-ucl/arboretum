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

import multiprocessing

import numpy as np

from scipy.ndimage.measurements import label
from scipy.ndimage.measurements import center_of_mass

import btrack

class _Stack:
    """ _Stack

    treat an image stack as a python iterator to enable multiprocessing.Pool
    to function on the stack.

    """
    def __init__(self, data):

        # basic assertions on the data
        assert(isinstance(data, np.ndarray))
        assert(data.dtype == np.uint8)

        self._stack = data
        self._idx = 0

    def __iter__(self): return self
    def __next__(self):
        if self._idx >= self._stack.shape[0]:
            raise StopIteration
        current = self._idx
        self._idx += 1
        return stack_as_array[current,...]

def _localize_process(image):
    """ worker process for localizing object """
    labeled, _ = label(image)
    centroids = center_of_mass(image, labeled)
    return centroids

def localize(stack_as_array,
             num_workers=8):
    """ localize

    get the centroids of all objects given a segmentaion mask from Napari

    Parameters:
        stack_as_array: a numpy array of the stack, typically the data from
            a napari 'labels' layer
        num_workers: number of processes to distribute the job accross

    TODO:
        - have this work with a three dimensional volume
        - use the segmentation to add labels to objects for the tracker
    """

    stack = _Stack(stack_as_array)

    with multiprocessing.Pool(num_workers) as pool:
        localizations = pool.map(_localize_process, stack)

    return [(i,)+localizations[i]+(0,) for i in range(len(localizations))]


def track(localizations,
          config_filename,
          volume=((0,1200),(0,1600),(-1e5,1e5)),
          optimize=True):

    """ track

    Run BayesianTracker with the localizations from the localize function

    """

    # convert the localizations into btrack objects
    from btrack.dataio import ObjectFactory
    ObjectFactory.reset() # belt and braces, reset ID counter to zero
    objects = [ObjectFactory.get(o) for o in localizations]

    # initialise a tracker session using a context manager
    with btrack.BayesianTracker() as tracker:

        # configure the tracker using a config file, append objects and set vol
        tracker.configure_from_file(config_filename)
        tracker.append(objects)
        tracker.volume = volume

        # track them and (optionally) optimize
        tracker.track_interactive(step_size=100)
        if optimize: tracker.optimize()

        # get the tracks as a python list
        tracks = tracker.tracks

    return tracks
