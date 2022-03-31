from napari import layers

from napari_arboretum import Arboretum, load_sample_data


def test_plugin(make_napari_viewer):
    """
    A simple smoke test for drawing the graph. Note that this checks the code
    works, not that the correct graph is drawn!
    """
    viewer = make_napari_viewer()
    tracks, segmentation = load_sample_data()

    plugin = Arboretum(viewer)
    plugin.draw_graph(tracks, 140)
