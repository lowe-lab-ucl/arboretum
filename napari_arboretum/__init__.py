try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"

from ._hookimpls import napari_experimental_provide_dock_widget
from .plugin import Arboretum
from .sample import load_sample_data
