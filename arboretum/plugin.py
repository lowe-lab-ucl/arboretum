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
import pyqtgraph as pg

from qtpy.QtWidgets import (
    QButtonGroup,
    QWidget,
    QPushButton,
    QSlider,
    QCheckBox,
    QLabel,
    QSpinBox,
    QHBoxLayout,
    QVBoxLayout,
    QFileDialog,
    QComboBox,
    QGridLayout,
    QGroupBox,
)

from qtpy.QtCore import Qt

import btrack
from btrack.constants import BayesianUpdates

from . import utils
from .io import TrackerFrozenState
from .tree import _build_tree_graph
from .layers.tracks import Tracks

from typing import Union
from napari.layers import Labels
from napari._qt.widgets.qt_range_slider import QHRangeSlider


DEFAULT_PATH = os.getcwd()
GUI_MAXIMUM_WIDTH = 225
GUI_MAXIMUM_HEIGHT = 350
GUI_MINIMUM_HEIGHT = 300






class Arboretum(QWidget):

    """ Arboretum

    A track visualization and lineage tree plotter integration for Napari.

    """

    def __init__(self, *args, **kwargs):

        super(Arboretum, self).__init__(*args, **kwargs)

        layout = QVBoxLayout()


        # add some buttons
        self.load_button = QPushButton('Load...', self)
        self.config_button = QPushButton('Configure...', self)
        self.localize_button = QPushButton('Localize', self)
        self.track_button = QPushButton('Track', self)
        self.save_button = QPushButton('Save...', self)


        # checkboxes
        self.optimize_checkbox = QCheckBox()
        self.optimize_checkbox.setChecked(True)
        # self.use_states_checkbox = QCheckBox()
        # self.use_states_checkbox.setChecked(True)


        # combo boxes
        self.tracking_mode_combobox = QComboBox()
        for mode in BayesianUpdates:
            self.tracking_mode_combobox.addItem(mode.name.lower())
        default_mode = BayesianUpdates.EXACT
        self.tracking_mode_combobox.setCurrentIndex(default_mode.value)


        # # sliders
        self.search_radius_slider = QSlider(Qt.Horizontal)
        self.search_radius_slider.setFocusPolicy(Qt.NoFocus)
        self.search_radius_slider.setMinimum(1)
        self.search_radius_slider.setMaximum(300)
        self.search_radius_slider.setSingleStep(1)
        # self.search_radius_slider.setEnabled(False)


        # dynamic labels
        self.config_filename_label = QLabel()
        self.localizations_label = QLabel()
        self.tracks_label = QLabel()
        self.status_label = QLabel()
        self.search_radius_label = QLabel()
        self.search_radius_label.setAlignment(Qt.AlignRight)

        # load/save buttons
        io_panel = QWidget()
        io_layout = QHBoxLayout()
        io_layout.addWidget(self.load_button)
        io_layout.addWidget(self.save_button)
        io_panel.setLayout(io_layout)
        io_panel.setMaximumWidth(GUI_MAXIMUM_WIDTH)
        layout.addWidget(io_panel)

        # tracking panel
        tracking_panel = QGroupBox('tracking')
        tracking_layout = QGridLayout()
        tracking_layout.addWidget(QLabel('method: '), 0, 0)
        tracking_layout.addWidget(self.tracking_mode_combobox, 0, 1)
        tracking_layout.addWidget(self.search_radius_label, 1, 0)
        tracking_layout.addWidget(self.search_radius_slider, 1, 1)
        tracking_layout.addWidget(QLabel('optimize: '), 2, 0)
        tracking_layout.addWidget(self.optimize_checkbox, 2, 1)
        tracking_layout.addWidget(self.config_button, 3, 0)
        tracking_layout.addWidget(self.config_filename_label, 3, 1)
        tracking_layout.addWidget(self.localize_button, 4, 0)
        tracking_layout.addWidget(self.localizations_label, 4, 1)
        tracking_layout.addWidget(self.track_button, 5, 0)
        tracking_layout.addWidget(self.tracks_label, 5, 1)
        tracking_layout.setColumnMinimumWidth(1, 150)
        tracking_layout.setSpacing(4)
        tracking_panel.setMaximumWidth(GUI_MAXIMUM_WIDTH)
        tracking_panel.setLayout(tracking_layout)
        layout.addWidget(tracking_panel)

        # status panel
        status_panel = QGroupBox('status')
        status_layout = QHBoxLayout()
        status_layout.addWidget(self.status_label)
        status_panel.setMaximumWidth(GUI_MAXIMUM_WIDTH)
        status_panel.setLayout(status_layout)
        layout.addWidget(status_panel)

        # set the layout
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(4)

        self.setLayout(layout)
        self.setMaximumHeight(GUI_MAXIMUM_HEIGHT)
        self.setMaximumWidth(GUI_MAXIMUM_WIDTH)

        # callbacks
        self.load_button.clicked.connect(self.load_data)
        self.save_button.clicked.connect(self.export_data)
        self.config_button.clicked.connect(self.load_config)
        self.tracking_mode_combobox.currentTextChanged.connect(self._on_mode_change)
        self.search_radius_slider.valueChanged.connect(self._on_radius_change)


        self._tracker_state = None

        self._segmentation = None
        self._localizations = None
        self._tracks = None
        self._btrack_cfg = None
        self._active_layer = None

        # TODO(arl): this is the working filename for the dataset
        self.filename = None
        self._search_radius = None

        self._on_mode_change()
        self.search_radius_slider.setValue(100)




    def load_data(self):
        """ load data in hdf or json format from btrack """
        filename = QFileDialog.getOpenFileName(self,
                                               'Open tracking data',
                                               DEFAULT_PATH,
                                               'Tracking files (*.hdf5 *.h5)')
        # only load file if we actually chose one
        if filename[0]:
            self.filename = filename[0]
        else:
            self.filename = None


    def load_config(self):
        """ load a btrack configuration file """
        filename = QFileDialog.getOpenFileName(self,
                                               'Open tracking config',
                                               DEFAULT_PATH,
                                               'Tracking files (*.json)')
        # only load file if we actually chose one
        if filename[0]:
            self.btrack_cfg = utils._get_btrack_cfg(filename=filename[0])
        else:
            self.btrack_cfg = None


    def export_data(self):
        """ export track data """
        export_fn = os.path.join(DEFAULT_PATH, 'tracks.h5')
        filename = QFileDialog.getSaveFileName(self,
                                               'Export tracking data',
                                               export_fn,
                                               'Tracking files (*.h5, *.csv)')
        # only export file if we actually chose one
        if filename[0]:
            filename, ext = os.path.splitext(filename[0])
            if ext == '.h5':
                utils.export_hdf(f'{filename}.h5',
                                 self.segmentation,
                                 self.tracker_state)
            elif ext == '.csv':
                btrack.dataio.export_CSV(f'{filename}.csv', self.tracker_state)

    @property
    def ndim(self):
        return self.segmentation.ndim


    @property
    def tracker_state(self) -> TrackerFrozenState:
        return self._tracker_state

    @tracker_state.setter
    def tracker_state(self, state: TrackerFrozenState):
        self._tracker_state = state
        self.tracks = [state.tracks]

    @property
    def segmentation(self) -> np.ndarray:
        return self._segmentation

    @segmentation.setter
    def segmentation(self, segmentation: Union[np.ndarray, Labels]):
        if segmentation is None:
            self._segmentation = None
            return
        elif isinstance(segmentation, np.ndarray):
            self._segmentation = segmentation
        else:
            # assume this is a napari layer
            self._segmentation = segmentation.data

        # TODO(arl): check that we deal with multidimensional data correctly
        assert(self._segmentation.ndim<5)

    @property
    def tracks(self) -> list:
        return self._tracks

    @tracks.setter
    def tracks(self, tracks):
        self._tracks = tracks

        n_tracks = sum([len(t) for t in tracks])
        n_tracks_str = f'{n_tracks} tracks'
        self.tracks_label.setText(n_tracks_str)

    @property
    def localizations(self) -> np.ndarray:
        return self._localizations

    @localizations.setter
    def localizations(self, localizations: np.ndarray):
        self._localizations = localizations
        n_localizations_str = f'{localizations.shape[0]} objects'
        self.localizations_label.setText(n_localizations_str)


    @property
    def btrack_cfg(self) -> dict:
        return self._btrack_cfg

    @btrack_cfg.setter
    def btrack_cfg(self, cfg: dict):
        self._btrack_cfg = cfg
        truncate_fn = lambda f: f'...{f[-20:]}'
        self.config_filename_label.setText(truncate_fn(cfg['Filename']))

    @property
    def volume(self) -> tuple:
        """ get the volume to use for tracking """
        if self.segmentation is None:
            return ((0,1200), (0,1600), (-1e5,1e5))
        else:
            volume = []
            # assumes time is the first dimension
            for dim in self.segmentation.shape[-2:]:
                volume.append((0, dim))
            #
            # if len(volume) == 2:
            volume.append((-1e5, 1e5))

            return tuple(volume)

    @property
    def active_layer(self) -> str:
        if self._active_layer is None: return ''
        return self._active_layer

    @active_layer.setter
    def active_layer(self, layer_name: str):
        self._active_layer = layer_name

    @property
    def tracking_mode(self) -> BayesianUpdates:
        return self._tracking_mode

    @tracking_mode.setter
    def tracking_mode(self, mode: BayesianUpdates):
        self._tracking_mode = mode

    @property
    def optimize(self) -> bool:
        return self.optimize_checkbox.isChecked()

    @property
    def search_radius(self) -> int:
        return self._search_radius
        # if self.tracking_mode == BayesianUpdates.APPROXIMATE:
        #     return self._search_radius
        # else:
        #     return None

    def _on_mode_change(self, event=None):
        mode = self.tracking_mode_combobox.currentText().upper()
        self.tracking_mode = BayesianUpdates[mode]
        # if self.tracking_mode == BayesianUpdates.APPROXIMATE:
        #     self.search_radius_slider.setEnabled(True)
        # else:
        #     self.search_radius_slider.setEnabled(False)

    def _on_radius_change(self, value):
        self.search_radius_label.setText(f'{value}')
        self._search_radius = value


    def get_tree(self, track_id: int):
        """ get a tree associated with this track """
        print(f'Selected track: {track_id}')

        if track_id:

            # test, plot the track we've selected
            selected_track = filter(lambda t: t.ID == track_id, self.tracks[0])
            track = list(selected_track)[0]

            # get the root node?
            root = [t for t in self.tracks[0] if t.ID == track.root]
            if root:
                root = root[0]
            else:
                return

            return (track_id,) + tuple(_build_tree_graph(root, self.tracks[0]))

        return




class ArboretumTreeViewer(QWidget):
    """ separate tree viewer widget """
    def __init__(self, *args, **kwargs):
        super(ArboretumTreeViewer, self).__init__(*args, **kwargs)
        layout = QVBoxLayout()
        plot_widget = pg.GraphicsLayoutWidget()
        self.plot_view = plot_widget.addPlot(title='Lineage tree',
                                             labels={'left': 'Time'})
        self.plot_view.hideAxis('bottom')
        layout.addWidget(plot_widget)
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(4)
        self.setLayout(layout)


    def plot_tree(self, track_id, edges, markers, annotations):

        self.clear()

        self.plot_view.setTitle(f'Lineage tree: {track_id}')

        for ex, ey, ec in edges:
            self.plot_view.plot(ex, ey, pen=pg.mkPen(color=ec, width=3))

        # labels
        for tx, ty, tstr, tcol in annotations:

            if tstr == str(track_id):
                tcol[3] = 255
            else:
                tcol[3] = 64

            pt = pg.TextItem(text=tstr,
                             color=tcol,
                             html=None,
                             anchor=(0, 0),
                             border=None,
                             fill=None,
                             angle=0,
                             rotateAxis=None)
            pt.setPos(tx, ty)
            self.plot_view.addItem(pt, ignoreBounds=True)

    def clear(self):
        self.plot_view.clear()
