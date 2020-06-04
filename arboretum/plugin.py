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
# import pyqtgraph as pg

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

from qtpy import QtCore

import btrack

from . import utils
from .tree import _build_tree_graph
from .layers.tracks import Tracks

import matplotlib.pyplot as plt

from typing import Union
from napari.layers import Labels
from napari._qt.qt_range_slider import QHRangeSlider


cmap = plt.cm.get_cmap('prism')
COLOR_CYCLE = lambda x: np.array(cmap(np.mod(x, 32) * 8))


DEFAULT_PATH = os.getcwd()



"""
initial_values : 2-tuple, optional
        Initial min & max values of the slider, defaults to (0.2, 0.8)
    data_range : 2-tuple, optional
        Min and max of the slider range, defaults to (0, 1)
    step_size : float, optional
        Single step size for the slider, defaults to 1
    collapsible : bool
        Whether the slider is collapsible, defaults to True.
    collapsed : bool
        Whether the slider begins collapsed, defaults to False.
    parent : qtpy.QtWidgets.QWidget
        Parent widget.
        """



class Arboretum(QWidget):

    """ Arboretum

    A track visualization and lineage tree plotter integration for Napari.

    """

    def __init__(self, *args, **kwargs):

        super(Arboretum, self).__init__(*args, **kwargs)

        layout = QGridLayout()

        # add some buttons
        self.load_button = QPushButton('Load...', self)
        self.config_button = QPushButton('Configure...', self)
        self.localize_button = QPushButton('Localize', self)
        self.track_button = QPushButton('Track', self)
        self.save_button = QPushButton('Save...', self)

        # checkboxes
        self.optimize_checkbox = QCheckBox()
        self.optimize_checkbox.setChecked(True)

        # # sliders
        # self.track_filter_slider = QHRangeSlider(initial_values=(1,3000),
        #                                         data_range=(1,3000),
        #                                         step_size=1,
        #                                         parent=self)

        # dynamic labels
        self.config_filename_label = QLabel()
        self.localizations_label = QLabel()
        self.tracks_label = QLabel()
        self.status_label = QLabel()

        layout.addWidget(self.load_button, 0, 0)
        layout.addWidget(self.save_button, 0, 1)


        # tracking panel
        tracking_panel = QGroupBox('Tracking')
        tracking_layout = QGridLayout()
        tracking_layout.addWidget(QLabel('Optimize:'), 0, 0)
        tracking_layout.addWidget(self.optimize_checkbox, 0, 1)
        tracking_layout.addWidget(self.config_button, 2, 0)
        tracking_layout.addWidget(self.config_filename_label, 2, 1)
        tracking_layout.addWidget(self.localize_button, 3, 0)
        tracking_layout.addWidget(self.localizations_label, 3, 1)
        tracking_layout.addWidget(self.track_button, 4, 0)
        tracking_layout.addWidget(self.tracks_label, 4, 1)
        tracking_layout.setColumnMinimumWidth(1, 150)
        tracking_panel.setLayout(tracking_layout)
        layout.addWidget(tracking_panel, 1, 0, 1, 2)

        layout.addWidget(QLabel('Status:'), 7, 0, 1, 2)
        layout.addWidget(self.status_label, 7, 1, 1, 2)
        layout.setAlignment(QtCore.Qt.AlignTop)
        layout.setSpacing(4)
        self.setLayout(layout)

        self.load_button.clicked.connect(self.load_data)
        self.save_button.clicked.connect(self.export_data)
        self.config_button.clicked.connect(self.load_config)

        self._segmentation = None
        self._localizations = None
        self._tracks = None
        self._btrack_cfg = None
        self._active_layer = None

        # TODO(arl): this is the working filename for the dataset
        self.filename = None


    def load_data(self):
        """ load data in hdf or json format from btrack """
        filename = QFileDialog.getOpenFileName(self,
                                               'Open tracking data',
                                               DEFAULT_PATH,
                                               'Tracking files (*.hdf5 *.json)')
        # only load file if we actually chose one
        if filename[0]:
            self.filename = filename[0]



    def load_config(self):
        """ load a btrack configuration file """
        filename = QFileDialog.getOpenFileName(self,
                                               'Open tracking config',
                                               DEFAULT_PATH,
                                               'Tracking files (*.json)')
        # only load file if we actually chose one
        if filename[0]:
            self.btrack_cfg = utils._get_btrack_cfg(filename=filename[0])

    def export_data(self):
        """ export track data """
        filename = QFileDialog.getSaveFileName(self,
                                               'Export tracking data',
                                               DEFAULT_PATH,
                                               'Tracking files (*.json)')
        # only load file if we actually chose one
        if filename[0] and self.tracks is not None:
            # for track_set in self.tracks:
            export_dir, fn = os.path.split(filename[0])
            btrack.dataio.export_all_tracks_JSON(export_dir,
                                                 self.tracks[0],
                                                 as_zip_archive=True)



    @property
    def segmentation(self) -> np.ndarray:
        return self._segmentation

    @segmentation.setter
    def segmentation(self, segmentation: Union[np.ndarray, Labels]):
        if isinstance(segmentation, np.ndarray):
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
        print(cfg, type(cfg))
        self._btrack_cfg = cfg
        truncate_fn = lambda f: f'...{f[-20:]}'
        self.config_filename_label.setText(truncate_fn(cfg['Filename']))

    @property
    def volume(self):
        """ get the volume to use for tracking """
        if self.segmentation is None:
            return ((0,1200), (0,1600), (-1e5,1e5))
        else:
            volume = []
            # assumes time is the first dimension
            for dim in self.segmentation.shape[1:]:
                volume.append((0, dim))

            if len(volume) == 2:
                volume.append((-1e5, 1e5))

            return tuple(volume)


    @property
    def active_layer(self) -> str:
        if self._active_layer is None: return ''
        return self._active_layer

    @active_layer.setter
    def active_layer(self, layer_name: str):
        self._active_layer = layer_name
