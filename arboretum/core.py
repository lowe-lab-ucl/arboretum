
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

from .plugin import Arboretum

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



def build_manager(tracks):
    """ build the track manager """
    return TrackManager(tracks)



def build_plugin(viewer, manager):

    # register the custom layers with this napari instance
    _register_tracks_layer()

    # add the arboretum tracks layer
    track_layer = Tracks(name='Tracks', manager=manager)
    viewer.add_layer(track_layer)

    # # build the plugin
    # arbor = Arboretum(manager, track_layer)
    # arbor.update(clear=False)
    # arbor.plot_cell_count()
    #
    # # add the widget
    # viewer.window.add_dock_widget(arbor.widget,
    #                               name='arboretum',
    #                               area='right')

    # def update_slider(event):
    #     # only trigger if update comes from first axis (optional)
    #     if event.axis == 0:
    #         idx = viewer.dims.indices[0]
    #         arbor.update_frame_indicator(idx)
    #
    # viewer.dims.events.axis.connect(update_slider)
