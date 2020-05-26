from vispy.scene.visuals import Markers
from vispy.scene.visuals import Line
from vispy.scene.visuals import Text
from vispy.scene.visuals import Compound

from napari._vispy.vispy_base_layer import VispyBaseLayer

import numpy as np

from ._track_shader import TrackShader

class VispyTracksLayer(VispyBaseLayer):
    """ VispyTracksLayer

    Custom napari Track layer for visualizing tracks.

    """
    def __init__(self, layer):
        # node = Line()
        node = Compound([Line(), Markers(), Text(method='gpu')])
        super().__init__(layer, node)

        self.layer.events.edge_width.connect(self._on_data_change)
        self.layer.events.tail_length.connect(self._on_data_change)
        self.layer.events.display_id.connect(self._on_data_change)
        self.layer.events.color_by.connect(self._on_color_by)

        # if the dimensions change, we need to update the data
        self.layer.dims.events.ndisplay.connect(self._on_dimensions_change)

        # build and attach the shader to the track
        self.shader = TrackShader(current_time=0,
                                  tail_length=self.layer.tail_length,
                                  vertex_time_vector=self.layer.manager._data[:,0])

        node._subvisuals[0].attach(self.shader)
        # node._subvisuals[1].attach(self.shader)

        # now set the data for the track lines
        self._positions = self.layer.data
        self.node._subvisuals[0].set_data(pos=self._positions,
                                          color=self.layer.manager.track_colors,
                                          connect=self.layer.manager.track_connex)

        # # add markers for each time point
        # self.node._subvisuals[1].set_data(pos=self._positions,
        #                                   size=4,
        #                                   edge_color=((0.,0.,0.,0.)),
        #                                   face_color=self.layer.manager.track_colors,
        #                                   scaling=False)

        self.node._subvisuals[2].color = 'white'
        self.node._subvisuals[2].font_size = 8

        self._reset_base()
        self._on_data_change()

    def _on_data_change(self, event=None):
        """ update the display

        NOTE(arl): this gets called by the VispyBaseLayer

        """
        # update the shader
        self.shader.current_time = self.layer.current_frame
        self.shader.tail_length = self.layer.tail_length
        self.node._subvisuals[0].set_data(width=self.layer.edge_width)

        # update the track IDs
        self.node._subvisuals[2].visible = self.layer.display_id
        if self.node._subvisuals[2].visible:
            self.node._subvisuals[2].text = self.layer.manager.object_IDs(self.layer.current_frame)
            self.node._subvisuals[2].pos = self.layer.manager.object_pos(self.layer.current_frame)

        self.node.update()
        # Call to update order of translation values with new dims:
        self._on_scale_change()
        self._on_translate_change()


    def _on_dimensions_change(self, event=None):
        """ if we change dimensions, change the display of the tracks """
        print(self.layer.dims.displayed)


    def _on_color_by(self, event=None):
        """ change the coloring only """
        self.node._subvisuals[0].set_data(color=self.layer.manager.track_colors)
        # self.node._subvisuals[1].set_data(face_color=self.layer.manager.track_colors)
        self.node.update()
        # Call to update order of translation values with new dims:
        self._on_scale_change()
        self._on_translate_change()
