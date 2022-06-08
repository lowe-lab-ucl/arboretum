import numpy as np
import pytest
from napari import layers

from napari_arboretum import Arboretum, load_sample_data


@pytest.fixture
def viewer_plugin(make_napari_viewer):
    """
    - Create a a napari viewer
    - Add sample tracks and segmentation
    - Add an Arboretum widget
    - Return the viewer and plugin
    """
    viewer = make_napari_viewer()
    tracks, segmentation = load_sample_data()
    viewer.add_layer(tracks)
    viewer.add_layer(segmentation)

    plugin = Arboretum(viewer)
    plugin.tracks = tracks

    return viewer, plugin


def test_plugin(viewer_plugin):
    """
    A simple smoke test for drawing the graph. Note that this checks the code
    works, not that the correct graph is drawn!
    """
    viewer, plugin = viewer_plugin
    # Setting this property automatically triggers graph drawing
    plugin.track_id = 140


def test_colormap_change(viewer_plugin):
    """
    Check that arboretum widget colours change when the track colourmap
    is changed.
    """
    viewer, plugin = viewer_plugin
    id = 140
    plugin.track_id = id

    tree = plugin.plotter.tree
    old_color = tree.get_branch_color(branch_id=id)

    # Change the colormap
    assert viewer.layers[0].colormap != "viridis"
    viewer.layers[0].colormap = "viridis"

    # Check that color has changed
    new_color = tree.get_branch_color(branch_id=id)
    # Slice to remove alpha, which is 1 both before and after
    assert np.all(new_color[:, :3] != old_color[:, :3])


def test_colorby_change(viewer_plugin):
    """
    Check that arboretum widget colours change when the attribute that the
    track is coloured by changes.
    """
    viewer, plugin = viewer_plugin
    id = 140
    plugin.track_id = id

    tree = plugin.plotter.tree
    old_color = tree.get_branch_color(branch_id=id)

    # Change the color by attribute
    assert viewer.layers[0].color_by != "generation"
    viewer.layers[0].color_by = "generation"

    # Check that color has changed
    new_color = tree.get_branch_color(branch_id=id)
    # Slice to remove alpha, which is 1 both before and after
    assert np.all(new_color[:, :3] != old_color[:, :3])
