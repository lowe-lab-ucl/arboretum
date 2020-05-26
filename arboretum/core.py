
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




def build_plugin_v2(viewer):

    from .plugin import Arboretum

    # register the custom layers with this napari instance
    _register_tracks_layer()

    # build the plugin
    arbor = Arboretum()

    # add the widget to Napari
    viewer.window.add_dock_widget(arbor,
                                  name='arboretum',
                                  area='right')


    # callbacks to add layers
    def add_segmentation_layer():
        """ add a segmentation layer """
        if arbor.segmentation is not None:
            seg_layer = viewer.add_labels(arbor.segmentation, name='Segmentation')
            seg_layer.editable = False

    def add_localizations_layer():
        """ add a localizations layer """
        if arbor.localizations is not None:
            pts_layer = viewer.add_points(arbor.localizations[:,:3], name='Localizations')

    def add_track_layer():
        """ add a track layer """
        if arbor.tracks is not None:
            for i, track_set in enumerate(arbor.tracks):
                _trk_layer = Tracks(manager=TrackManager(track_set), name=f'Tracks {i}')
                track_layer = viewer.add_layer(_trk_layer)


    # if we loaded some data add both the segmentation and tracks layer
    arbor.load_button.clicked.connect(add_segmentation_layer)
    arbor.load_button.clicked.connect(add_track_layer)
