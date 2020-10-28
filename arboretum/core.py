# ------------------------------------------------------------------------------
# Name:     Arboretum
# Purpose:  Dockable widget, and custom track visualization layers for Napari,
#           to cell/object track data.
#
# Authors:  Alan R. Lowe (arl) a.lowe@ucl.ac.uk
#
# License:  See LICENSE.md
#
# Created:  01/05/2020
# ------------------------------------------------------------------------------

import napari

from .plugin import ArboretumTreeViewer

PLUGIN_NAME = "arboretum"


def build_plugin(viewer: napari.Viewer):
    """Build the arboretum plugin."""
    widget = ArboretumTreeViewer(viewer)
    return widget


if __name__ == "__main__":
    pass
