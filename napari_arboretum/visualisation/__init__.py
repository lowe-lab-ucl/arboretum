"""
Code for creating tree visualisations.

`base_plotter` contains `TreePlotterBase`, a base class for plotting trees.
This base class is backend independent, which means it does not depend on
a specific plotting library (e.g. pyqtgraph, Matplotlib, vispy).

To implement a usable plotting class `TreePlotterBase` can be inherited,
and plotting-library-specific functionality defined in the abstract methods
that must be implemented.
"""

from .base_plotter import *
from .matplotlib_plotter import *
from .vispy_plotter import *
