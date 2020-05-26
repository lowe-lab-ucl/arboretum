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

from scipy.ndimage import measurements

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
        return self._stack[current,...], current

def _localize_process(data) -> np.ndarray:
    # image: np.ndarray, frame: int) -> np.ndarray:
    """ worker process for localizing and labelling objects

    Returns:
        combined data in form of nx5 array (t, x, y, z, label) adding a
        z-dimension of uniform zero, if one doesn't exist.
    """
    image, frame = data
    labeled, n = measurements.label(image.astype(np.bool))
    idx = list(range(1, n+1))
    centroids = np.array(measurements.center_of_mass(image, labels=labeled, index=idx))
    labels = np.array(measurements.maximum(image, labels=labeled, index=idx))


    localizations = np.zeros((centroids.shape[0], 5), dtype=np.float32)
    localizations[:,0] = frame # time
    localizations[:,1:centroids.shape[1]+1] = centroids
    localizations[:,-1] = labels-1 #-1 because we use a label of zero for states

    return localizations

def localize(stack_as_array: np.ndarray,
             num_workers: int = 8):
    """ localize

    get the centroids of all objects given a segmentaion mask from Napari.

    Should work with volumetric data, and infers the object class label from
    the segmentation label.

    Parameters:
        stack_as_array: a numpy array of the stack, typically the data from
            a napari 'labels' layer
        num_workers: number of processes to distribute the job accross
    """

    stack = _Stack(stack_as_array)

    with multiprocessing.Pool(num_workers) as pool:
        localizations = pool.map(_localize_process, stack)

    return np.concatenate(localizations, axis=0)




def _track_process():
    pass


def track(localizations: np.ndarray,
          config_filename: str,
          volume: tuple = ((0,1200),(0,1600),(-1e5,1e5)),
          optimize: bool = True):

    """ track

    Run BayesianTracker with the localizations from the localize function

    """

    n_localizations = localizations.shape[0]
    idx = range(n_localizations)

    # convert the localizations into btrack objects
    from btrack.dataio import  _PyTrackObjectFactory
    factory = _PyTrackObjectFactory()
    objects = [factory.get(localizations[i,:4], label=int(localizations[i,-1])) for i in idx]

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



def load_hdf(filename: str,
             filter_by: str = 'area>=50',
             load_segmentation: bool = True):

    """ load data from an HDF file """
    with btrack.dataio.HDF5FileHandler(filename) as h:
        h._f_expr = filter_by
        tracks = h.tracks
        seg = h.segmentation

    return seg, tracks


def export_hdf(filename: str,
               tracker: btrack.BayesianTracker):
    """ export the tracking data to an hdf file """
    pass


if __name__ == '__main__':
    pass