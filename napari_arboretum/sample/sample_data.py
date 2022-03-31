"""
Functions to load sample data.

The sample data fetching/caching is handled by the `pooch` library. A registry
of files and their expected hashes is stored in :file:``registry.txt``.
"""

import json
import pathlib
from typing import Tuple

import napari.layers
import pandas as pd
import pooch
from skimage.io import imread

POOCH_BASE = "https://raw.githubusercontent.com/lowe-lab-ucl/btrack-examples/main/"
POOCH = pooch.create(
    path=pooch.os_cache("arboretum"), base_url=POOCH_BASE, registry=None
)

registry_file = pathlib.Path(__file__).parent / "registry.txt"
POOCH.load_registry(registry_file)


def load_sample_data() -> Tuple[napari.layers.Tracks, napari.layers.Labels]:
    """
    Load some sample data.

    Returns
    -------
    tracks : napari.layers.Tracks
    segmentation : napari.layers.Labels
    """
    # Load track data files
    track_data = pd.read_csv(POOCH.fetch("examples/tracks.csv", progressbar=True))
    properties = pd.read_csv(POOCH.fetch("examples/properties.csv", progressbar=True))
    with open(POOCH.fetch("examples/graph.json", progressbar=True)) as f:
        graph = json.load(f)
    # For some reason json reads keys as str, not int, so convert
    graph = {int(k): v for k, v in graph.items()}

    tracks = napari.layers.Tracks(
        track_data, properties=properties, graph=graph, name="btrack_sample"
    )

    # Load original segmentation
    segmenation_data = imread(POOCH.fetch("examples/segmented.tif", progressbar=True))
    segmentation = napari.layers.Labels(segmenation_data)

    return tracks, segmentation
