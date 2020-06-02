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

__author__ = 'Alan R. Lowe'
__email__ = 'code@arlowe.co.uk'

from vispy.visuals.filters.base_filter import Filter
from vispy.gloo import VertexBuffer

from typing import Union, List

import numpy as np

class TrackShader(Filter):
    """ TrackShader

    Custom vertex and fragment shaders for visualizing tracks quickly with
    vispy. The central assumption is that the tracks are rendered as a
    continuous vispy Line segment, with connections and colors defined when
    the visual is created.

    The shader simply changes the visibility and/or fading of the data according
    to the current_time and the associate time metadata for each vertex. This
    is scaled according to the tail length. Points ahead of the current time
    are rendered with alpha set to zero.

    Parameters:
        current_time: the current time, which is typically the frame index,
            although this can be an arbitrary float
        tail_length: the upper limit on length of the 'tail'
        vertex_time: a vector describing the time associated with each vertex

    TODO:
        - the track is still displayed, albeit with fading, once the track has
         finished but is still within the 'tail_length' window. Should it
         disappear?
        - check the shader positioning within the GL pipeline

    """

    VERT_SHADER = """
        varying vec4 v_track_color;
        void apply_track_shading() {

            float alpha;

            if ($a_vertex_time > $current_time) {
                // this is a hack to minimize the frag shader rendering ahead
                // of the current time point due to interpolation
                alpha = -100.0;
            } else {
                // fade the track into the temporal distance, scaled by the
                // maximum tail length from the gui
                float fade = ($current_time - $a_vertex_time) / $tail_length;
                alpha = clamp(1.0-fade, 0.0, 1.0);
            }

            // set the vertex alpha according to the fade
            v_track_color.a = alpha;
        }
    """

    FRAG_SHADER = """
        varying vec4 v_track_color;
        void apply_track_shading() {
            // interpolate
            gl_FragColor.a = v_track_color.a;
        }
    """

    def __init__(self,
                 current_time = 0,
                 tail_length = 30,
                 vertex_time: Union[List, np.ndarray] = []):

        super().__init__(vcode=self.VERT_SHADER, vpos=3,
                         fcode=self.FRAG_SHADER, fpos=9)

        self.current_time = current_time
        self.tail_length = tail_length
        self._vertex_time = vertex_time.reshape(-1 ,1).astype(np.float32)

    @property
    def current_time(self) -> Union[int, float]:
        return self._current_time

    @current_time.setter
    def current_time(self, n: Union[int, float]):
        self._current_time = n
        self.vshader['current_time'] = float(n)

    @property
    def tail_length(self) -> Union[int, float]:
        return self._tail_length

    @tail_length.setter
    def tail_length(self, l: Union[int, float]):
        self._tail_length = l
        self.vshader['tail_length'] = float(l)

    def _attach(self, visual):
        super(TrackShader, self)._attach(visual)
        self.vshader['a_vertex_time'] = VertexBuffer(self._vertex_time)