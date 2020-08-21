
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

EXPORT_PATH = '/media/quantumjot/Data/movie'


import os
import enum
import heapq

import btrack

import numpy as np

import napari
from napari.qt.threading import thread_worker

from multiprocessing import Process, SimpleQueue

from typing import Union

from . import utils
from .plugin import Arboretum, ArboretumTreeViewer
from .manager import TrackManager, tform_planar, tform_volumetric
from .layers.tracks import Tracks
from ._colormaps import colormaps

PLUGIN_NAME = 'arboretum'
PLUGIN_VERSION = f'{PLUGIN_NAME} (btrack: v{btrack.__version__})'

def _register_tracks_layer():
    """ _register_tracks_layer

    This can be used to register the custom arboretum Tracks layers with
    Napari.

    Notes:
        This is HACKTASTIC!

    """
    from .layers.tracks.vispy_tracks_layer import VispyTracksLayer
    from .layers.tracks.qt_tracks_layer import QtTracksControls

    # NOTE(arl): use this code to register a vispy function for the tracks layer
    napari._vispy.utils.layer_to_visual[Tracks] = VispyTracksLayer
    napari._qt.layers.utils.layer_to_controls[Tracks] = QtTracksControls







def build_plugin(viewer, tracks):

    # register the custom layers with this napari instance
    _register_tracks_layer()

    # build a track manager
    if isinstance(tracks, TrackManager):
        manager = tracks
    else:
        manager = TrackManager(tracks)

    # add the arboretum tracks layer
    track_layer = Tracks(name='Tracks',
                         data=manager.data,
                         properties=manager.properties,
                         colormaps_dict=colormaps)
    viewer.add_layer(track_layer)




def build_plugin_v2(viewer,
                    segmentation: Union[None, np.ndarray] = None):
    """ build the plugin

    Arguments:
        viewer: an instance of the napari viewer
        segmentation: optional segmentation to be loaded as as a `labels` layer

    """

    # register the custom layers with this napari instance
    _register_tracks_layer()

    # build the plugin
    arbor = Arboretum()
    tree_viewer = ArboretumTreeViewer()

    # add the widget to Napari
    viewer.window.add_dock_widget(arbor,
                                  name=PLUGIN_VERSION,
                                  area='bottom')

    viewer.window.add_dock_widget(tree_viewer,
                                  name='arboretum-tree-viewer',
                                  area='bottom')

    # name a new layer using the source layer
    new_layer_name = lambda s: f'{s} {arbor.active_layer}'

    # callbacks to add layers
    def add_segmentation_layer(editable:bool = False):
        """ add a segmentation layer """
        if arbor.segmentation is not None:
            seg_layer = viewer.add_labels(arbor.segmentation, name='Segmentation')
            seg_layer.editable = editable

    def add_localizations_layer():
        """ add a localizations layer """
        if arbor.localizations is not None:

            if arbor.ndim == 4:
                loc = arbor.localizations[:, (0, 3, 1, 2)]
            else:
                loc = arbor.localizations[:, (0, 1, 2)]

            pts_layer = viewer.add_points(loc,
                                          name=new_layer_name('Localizations'),
                                          face_color='b')
    def add_track_layer():
        """ add a track layer """
        if arbor.tracks is not None:
            for i, track_set in enumerate(arbor.tracks):

                if arbor.ndim == 4:
                    transform = tform_volumetric
                else:
                    transform = tform_planar

                # build a track manager
                manager = TrackManager(track_set,
                                       transform=transform)

                _trk_layer = Tracks(name=new_layer_name(f'Tracks {i}'),
                                    data=manager.data,
                                    properties=manager.properties,
                                    colormaps_dict=colormaps)
                track_layer = viewer.add_layer(_trk_layer)

                @track_layer.mouse_drag_callbacks.append
                def show_tree(track_layer, event):
                    track_id = track_layer._get_value()
                    tree = arbor.get_tree(track_id)
                    if tree is not None:
                        tree_viewer.plot_tree(*tree)


    def add_layers(*layers):
        """ TODO(arl): oof """
        for layer in layers:
            layer()

    def import_objects():
        """ wrapper to load objects/tracks """

        @thread_worker
        def _import():
            """ import track data """
            # get the extension, and pick the correct file loader
            if arbor.filename is not None:
                arbor.status_label.setText('Loading...')
                seg, loc, tracks = utils.load_hdf(arbor.filename)
                arbor.segmentation = seg
                arbor.tracks = tracks
                arbor.localizations = loc
                arbor.status_label.setText('')




        def add_new_layers():
            """ note that, if the data has already been loaded, then the user
            goes to load again, but cancels - this creates duplicate layers
            """
            if arbor.filename is None: return
            add_layers(add_segmentation_layer,
                       add_localizations_layer,
                       add_track_layer)

        worker = _import()
        worker.returned.connect(add_new_layers)
        worker.start()



    def localize_objects():
        """ wrapper to localizer objects """

        @thread_worker
        def _localize():
            """ localize objects using the currently selected layer """
            arbor.active_layer = viewer.active_layer
            arbor.segmentation = viewer.layers[viewer.active_layer]
            arbor.status_label.setText('Localizing...')
            arbor.localizations = utils.localize(arbor.segmentation)
            arbor.status_label.setText('')

        worker = _localize()
        worker.returned.connect(add_localizations_layer)
        worker.start()





    def track_objects():
        """ wrapper to launch a tracking thread """

        config = arbor.btrack_cfg
        method = arbor.tracking_mode
        optimize = arbor.optimize
        volume = arbor.volume
        search_radius = arbor.search_radius

        @utils.process_worker
        def _track_process(*args, **kwargs):
            """ spawn a process to run the tracker """
            return utils.track(*args, **kwargs)


        @thread_worker
        def _track():
            """ track objects using a manager thread """
            if arbor.localizations is not None:
                arbor.status_label.setText('Tracking...')

                # launch the tracking as a separate process
                args = (arbor.localizations, config)
                kwargs = {'method': method,
                          'optimize': optimize,
                          'volume': volume,
                          'search_radius': search_radius}

                tracker_state = _track_process(*args, **kwargs)

                arbor.tracker_state = tracker_state
                arbor.status_label.setText('')

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


    @viewer.bind_key('m')
    def make_movie(viewer):
        """ make a movie """
        num_frames = int(viewer.dims.max_indices[0])
        def _make_movie():
            for i in range(num_frames+1):
                viewer.dims.set_point(0, i)
                fn = os.path.join(EXPORT_PATH, f'movie_{i}.png')
                image = viewer.screenshot(path=fn, canvas_only=False)

        _make_movie()








def run(**kwargs):
    """ run an instance of napari with the plugin """
    with napari.gui_qt():
        viewer = napari.Viewer()
        build_plugin_v2(viewer, **kwargs)
