import numpy as np
from btrack.constants import Fates, States
from napari.utils.colormaps import Colormap, AVAILABLE_COLORMAPS


def colormap_bins(cmap: Colormap):
    return np.linspace(-0.5, cmap.shape[0]-0.5, cmap.shape[0]+1)






class ModuloColormap(Colormap):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def map_modulo(self, values):
        return self.map(np.mod(values, self.colors.shape[0]))


# state colors:
# States.INTERPHASE = 0         -> grey
# States.PROMETAPHASE = 1       -> blue
# States.METAPHASE = 2          -> green
# States.ANAPHASE = 3           -> magenta
# States.APOPTOSIS = 4          -> red
# States.NULL = 5               -> orange
# States.DUMMY = 99             -> orange
STATE_COLORMAP = np.array([[0.5, 0.5, 0.5, 1.0],
                           [0.0, 0.0, 1.0, 1.0],
                           [0.0, 1.0, 0.0, 1.0],
                           [1.0, 0.0, 1.0, 1.0],
                           [1.0, 0.0, 0.0, 1.0],
                           [1.0, 0.65, 0.0, 1.0],
                           [1.0, 0.65, 0.0, 1.0]])

# fate colors:
# Fates.FALSE_POSITIVE = 0      ->
# Fates.INITIALIZE = 1
# Fates.TERMINATE = 2
# Fates.LINK = 3
# Fates.DIVIDE = 4
# Fates.APOPTOSIS = 5
# Fates.MERGE = 6
# Fates.EXTRUDE = 7
# Fates.INITIALIZE_BORDER = 10
# Fates.INITIALIZE_FRONT = 11
# Fates.INITIALIZE_LAZY = 12
# Fates.TERMINATE_BORDER = 20
# Fates.TERMINATE_BACK = 21
# Fates.TERMINATE_LAZY = 22
# Fates.DEAD = 666
# Fates.UNDEFINED = 999
FATE_COLORMAP = np.array([])

# Survivor -> cyan
# Deceased -> red
SURVIVOR_COLORMAP = np.array([[1.0, 0.0, 0.0, 1.0],
                              [0.0, 1.0, 0.8, 1.0]])


# steal some colors, mwah ha ha...
ID_COLORMAP = AVAILABLE_COLORMAPS['turbo'].colors
ID_COLORMAP = ID_COLORMAP[::4,:]


id_colormap = ModuloColormap(ID_COLORMAP,
                             controls=colormap_bins(ID_COLORMAP),
                             interpolation='zero',
                             name='tracking_id')

state_colormap = Colormap(STATE_COLORMAP,
                          controls=colormap_bins(STATE_COLORMAP),
                          interpolation='zero',
                          name='tracking_state')

survivor_colormap = Colormap(SURVIVOR_COLORMAP,
                             controls=colormap_bins(SURVIVOR_COLORMAP),
                             interpolation='zero',
                             name='tracking_survivors')



colormaps = {'ID': id_colormap,
             'parent': id_colormap,
             'root': id_colormap,
             'states': state_colormap,
             'survivor': survivor_colormap}
