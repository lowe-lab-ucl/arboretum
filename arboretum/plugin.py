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
)

from qtpy import QtCore

import btrack

from . import utils
from .tree import _build_tree_graph
from .layers.track.track import Tracks
from .layers.track._track_utils import TrackManager

import matplotlib.pyplot as plt

from typing import Union
from napari.layers import Labels


cmap = plt.cm.get_cmap('prism')
COLOR_CYCLE = lambda x: np.array(cmap(np.mod(x, 32) * 8))


DEFAULT_PATH = '/media/quantumjot/DataIII/Data/Giulia/GV0800/Pos12/Pos12_aligned/HDF'





class Arboretum(QWidget):

    """ Arboretum

    A track visualization and lineage tree plotter integration for Napari.

    """

    def __init__(self, *args, **kwargs):

        super(Arboretum, self).__init__(*args, **kwargs)

        layout = QGridLayout()

        # add some buttons
        self.load_button = QPushButton('Load', self)
        self.localize_button = QPushButton('Localize', self)
        self.track_button = QPushButton('Track', self)
        self.save_button = QPushButton('Save', self)

        # TODO(arl): add back the tree visualization

        layout.addWidget(self.load_button, 0, 0)
        layout.addWidget(self.localize_button, 0, 1)
        layout.addWidget(self.track_button, 0, 2)
        layout.addWidget(self.save_button, 0, 3)

        layout.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(layout)

        self.load_button.clicked.connect(self.load_data)
        self.save_button.clicked.connect(self.export_data)

        self._segmentation = None
        self._localizations = None
        self._tracks = None


    def load_data(self):
        filename = QFileDialog.getOpenFileName(self,
                                               'Open tracking data',
                                               DEFAULT_PATH,
                                               'Tracking files (*.hdf5)')

        if filename[0]:
            seg, tracks = utils.load_hdf(filename[0])

            self.segmentation = seg
            self._tracks = tracks

    def export_data(self):
        pass


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

    @property
    def tracks(self) -> np.ndarray:
        return self._tracks

    @property
    def localizations(self) -> np.ndarray:
        return self._localizations
