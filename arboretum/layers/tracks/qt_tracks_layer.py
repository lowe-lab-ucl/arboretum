from napari._qt.layers.qt_image_base_layer import QtLayerControls

from qtpy.QtCore import Qt, Slot
from qtpy.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QSlider,
    QAbstractButton,
)

import numpy as np


MAX_TAIL_LENGTH = 1500
MAX_TAIL_WIDTH = 40

class QtTracksControls(QtLayerControls):
    """Qt view and controls for the arboretum Tracks layer.

    Parameters
    ----------
    layer : arboretum.layers.Tracks
        An instance of a Tracks layer.

    Attributes
    ----------
    grid_layout : qtpy.QtWidgets.QGridLayout
        Layout of Qt widget controls for the layer.
    layer : arboretum.layers.Tracks
        An instance of a Tracks layer.

    """

    def __init__(self, layer):
        super().__init__(layer)

        self.layer.events.edge_width.connect(self._on_edge_width_change)
        self.layer.events.tail_length.connect(self._on_tail_length_change)

        # combo box for track coloring
        self.color_by_combobox = QComboBox()
        self.color_by_combobox.insertItem(0, 'track ID')
        self.color_by_combobox.insertItem(1, 'root ID')
        self.color_by_combobox.insertItem(2, 'parent ID')
        self.color_by_combobox.insertItem(3, 'state')

        # slider for track tail length
        self.tail_length_slider = QSlider(Qt.Horizontal)
        self.tail_length_slider.setFocusPolicy(Qt.NoFocus)
        self.tail_length_slider.setMinimum(1)
        self.tail_length_slider.setMaximum(MAX_TAIL_LENGTH)
        self.tail_length_slider.setSingleStep(1)

        # slider for track edge width
        self.edge_width_slider = QSlider(Qt.Horizontal)
        self.edge_width_slider.setFocusPolicy(Qt.NoFocus)
        self.edge_width_slider.setMinimum(1)
        self.edge_width_slider.setMaximum(MAX_TAIL_WIDTH)
        self.edge_width_slider.setSingleStep(1)

        # checkboxes for display
        self.id_checkbox = QCheckBox()
        self.tail_checkbox = QCheckBox()
        self.tail_checkbox.setChecked(True)


        self.edge_width_slider.valueChanged.connect(self.change_width)
        self.tail_length_slider.valueChanged.connect(self.change_tail_length)
        self.tail_checkbox.stateChanged.connect(self.change_display_tail)
        self.id_checkbox.stateChanged.connect(self.change_display_id)
        self.color_by_combobox.currentIndexChanged.connect(self.change_color_by)

        # grid_layout created in QtLayerControls
        # addWidget(widget, row, column, [row_span, column_span])
        self.grid_layout.addWidget(QLabel('color by:'), 0, 0)
        self.grid_layout.addWidget(self.color_by_combobox, 0, 1)
        self.grid_layout.addWidget(QLabel('blending:'), 1, 0)
        self.grid_layout.addWidget(self.blendComboBox, 1, 1)
        self.grid_layout.addWidget(QLabel('opacity:'), 2, 0)
        self.grid_layout.addWidget(self.opacitySlider, 2, 1)
        self.grid_layout.addWidget(QLabel('tail width:'), 3, 0)
        self.grid_layout.addWidget(self.edge_width_slider, 3, 1)
        self.grid_layout.addWidget(QLabel('tail length:'), 4, 0)
        self.grid_layout.addWidget(self.tail_length_slider, 4, 1)
        self.grid_layout.addWidget(QLabel('tail:'), 5, 0)
        self.grid_layout.addWidget(self.tail_checkbox, 5, 1)
        self.grid_layout.addWidget(QLabel('show ID:'), 6, 0)
        self.grid_layout.addWidget(self.id_checkbox, 6, 1)
        self.grid_layout.setRowStretch(7, 1)
        self.grid_layout.setColumnStretch(1, 1)
        self.grid_layout.setSpacing(4)

        self._on_tail_length_change()
        self._on_edge_width_change()




    def _on_edge_width_change(self, event=None):
        """Receive layer model edge line width change event and update slider.

        Parameters
        ----------
        event : qtpy.QtCore.QEvent, optional.
            Event from the Qt context, by default None.
        """
        with self.layer.events.edge_width.blocker():
            value = self.layer.edge_width
            value = np.clip(int(2 * value), 1, MAX_TAIL_WIDTH)
            self.edge_width_slider.setValue(value)

    def change_width(self, value):
        """Change edge line width of shapes on the layer model.

        Parameters
        ----------
        value : float
            Line width of shapes.
        """
        self.layer.edge_width = float(value) / 2.


    def _on_tail_length_change(self, event=None):
        """Receive layer model edge line width change event and update slider.

        Parameters
        ----------
        event : qtpy.QtCore.QEvent, optional.
            Event from the Qt context, by default None.
        """
        with self.layer.events.tail_length.blocker():
            value = self.layer.tail_length
            value = np.clip(value, 1, MAX_TAIL_LENGTH)
            self.tail_length_slider.setValue(value)

    def change_tail_length(self, value):
        """Change edge line width of shapes on the layer model.

        Parameters
        ----------
        value : float
            Line width of shapes.
        """
        self.layer.tail_length = value


    def change_display_tail(self, state):
        self.layer.display_tail = self.tail_checkbox.isChecked()

    def change_display_id(self, state):
        self.layer.display_id = self.id_checkbox.isChecked()

    def change_color_by(self, value):
        self.layer.color_by = value
