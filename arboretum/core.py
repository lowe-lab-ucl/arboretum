
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
import enum
import heapq

import numpy as np

import napari
from napari.qt.threading import thread_worker

from typing import Union

from .layers.track.track import Tracks
from .layers.track._track_utils import TrackManager


def _register_tracks_layer():
    """ _register_tracks_layer

    This can be used to register the custom arboretum Tracks layers with
    Napari.

    Notes:
        This is HACKTASTIC!

    """
    from .layers.track.vispy_tracks_layer import VispyTracksLayer
    from .layers.track.qt_tracks_layer import QtTracksControls

    # NOTE(arl): use this code to register a vispy function for the tracks layer
    napari._vispy.utils.layer_to_visual[Tracks] = VispyTracksLayer
    napari._qt.layers.utils.layer_to_controls[Tracks] = QtTracksControls







def build_plugin(viewer, tracks):

    # register the custom layers with this napari instance
    _register_tracks_layer()

    # build a track manager
    manager = TrackManager(tracks)

    # add the arboretum tracks layer
    track_layer = Tracks(name='Tracks', manager=manager)
    viewer.add_layer(track_layer)




def build_plugin_v2(viewer,
                    segmentation: Union[None, np.ndarray] = None):
    """ build the plugin

    Arguments:
        viewer: an instance of the napari viewer
        segmentation: optional segmentation to be loaded as as a `labels` layer

    """

    from .plugin import Arboretum
    from . import utils

    # register the custom layers with this napari instance
    _register_tracks_layer()

    # build the plugin
    arbor = Arboretum()

    # add the widget to Napari
    viewer.window.add_dock_widget(arbor,
                                  name='arboretum',
                                  area='right')

    # callbacks to add layers
    def add_segmentation_layer(editable:bool = False):
        """ add a segmentation layer """
        if arbor.segmentation is not None:
            seg_layer = viewer.add_labels(arbor.segmentation, name='Segmentation')
            seg_layer.editable = editable

    def add_localizations_layer():
        """ add a localizations layer """
        if arbor.localizations is not None:
            pts_layer = viewer.add_points(arbor.localizations[:,:3],
                                          name='Localizations',
                                          face_color='b')
    def add_track_layer():
        """ add a track layer """
        if arbor.tracks is not None:
            for i, track_set in enumerate(arbor.tracks):
                _trk_layer = Tracks(manager=TrackManager(track_set), name=f'Tracks {i}')
                track_layer = viewer.add_layer(_trk_layer)


    def import_objects():
        """ wrapper to load objects/tracks """

        @thread_worker
        def _import():
            """ import data """
            # get the extension
            _, ext = os.path.splitext(arbor.filename)

            if ext in ('.hdf5',):
                seg, tracks = utils.load_hdf(arbor.filename)
                arbor.segmentation = seg
                arbor.tracks = tracks
            elif ext in ('.json',):
                tracks = utils.load_json(arbor.filename)
                arbor.tracks = [tracks]

        worker = _import()
        worker.returned.connect(add_segmentation_layer)
        worker.returned.connect(add_track_layer)



    def localize_objects():
        """ wrapper to localizer objects """

        @thread_worker
        def _localize():
            """ localize objects using the currently selected layer """
            arbor.segmentation = viewer.layers[viewer.active_layer]
            arbor.localizations = utils.localize(arbor.segmentation)

        worker = _localize()
        worker.returned.connect(add_localizations_layer)
        worker.start()



    def track_objects():
        """ wrapper to launch a tracking thread """

        #TODO(arl): infer the tracking volume from the image data

        @thread_worker
        def _track():
            """ track objects """
            if arbor.localizations is not None:
                tracks = utils.track(arbor.localizations,
                                     arbor.btrack_cfg,
                                     volume=arbor.volume)
                arbor.tracks = [tracks]

        worker = _track()
        worker.returned.connect(add_track_layer)
        worker.start()





    # if we loaded some data add both the segmentation and tracks layer
    arbor.load_button.clicked.connect(import_objects)

    # do some localization using the currently selected segmentation
    arbor.localize_button.clicked.connect(localize_objects)

    # do some tracking using the currently selected localizations
    arbor.track_button.clicked.connect(track_objects)

    # if we're passing a segmentation, add it as a labels layer
    if segmentation is not None:
        arbor.segmentation = segmentation
        add_segmentation_layer(editable=True)





def run(**kwargs):
    """ run an instance of napari with the plugin """
    with napari.gui_qt():
        viewer = napari.Viewer()
        build_plugin_v2(viewer, **kwargs)
