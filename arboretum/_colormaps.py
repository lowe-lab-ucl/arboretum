import numpy as np

from matplotlib.cm import get_cmap
from matplotlib.colors import ListedColormap

from btrack.constants import Fates, States


class IndexedColormap:
    """ Simple Indexed Colormap """
    def __init__(self,
                 array,
                 enum=None):

        self.array = array

        if enum is not None:
            self.indices = [e.value for e in list(enum)]
        else:
            self.indices = list(range(array.shape[0]))

        assert(len(self.indices) == self.array.shape[0])
        assert(self.array.shape[1] == 4)
        assert(self.array.ndim == 2)

    def __call__(self, idx):
        idx = np.mod(idx, len(self)).tolist()
        return self.array[np.take(self.indices, idx),...]

    def __len__(self):
        return len(self.indices)


class ModuloColormap:
    """ ModuloColormap """
    def __init__(self,
                 cmap_name,
                 max_index=32):

        self.cmap_name = cmap_name
        self.max_index = max_index
        self.cmap = get_cmap(cmap_name)

    def __len__(self):
        return self.max_index

    def __call__(self, idx):
        return self.cmap(np.mod(idx, len(self)) / self.max_index)


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



SURVIVOR_COLORMAP = np.array([[1.0, 0.0, 0.0, 1.0],
                              [0.0, 1.0, 0.8, 1.0]])


# state_cmap = ListedColormap(STATE_COLORMAP)
# fate_cmap = ListedColormap(FATE_COLORMAP)

state_cmap = IndexedColormap(STATE_COLORMAP, enum=States)
# fate_cmap = IndexedColormap(FATE_COLORMAP, enum=Fates)
id_cmap = ModuloColormap('gist_rainbow', max_index=32)
survivor_cmap = IndexedColormap(SURVIVOR_COLORMAP)



colormaps = {'ID': id_cmap,
             'parent': id_cmap,
             'root': id_cmap,
             'states': state_cmap,
             'survivor': survivor_cmap}
