from napari import layers

from napari_arboretum import load_sample_data


def test_sample_data():
    tracks, segmentation = load_sample_data()

    assert isinstance(tracks, layers.Tracks)
    assert isinstance(segmentation, layers.Labels)
