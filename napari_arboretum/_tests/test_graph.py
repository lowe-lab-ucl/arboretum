import numpy as np
import pytest
from napari.layers import Tracks

from napari_arboretum import graph

TEST_GRAPH = {1: [0], 2: [0], 3: [1], 4: [1], 5: [2], 6: [2]}
TEST_GRAPH_REVERSE = {0: [1, 2], 1: [3, 4], 2: [5, 6]}
TEST_GRAPH_ROOT = 0
TEST_GRAPH_LINEAR = [0, 1, 2, 3, 4, 5, 6]


def test_reverse_graph():
    """Test that reversing the graph produces the correct output."""
    roots, reverse = graph.build_reverse_graph(TEST_GRAPH)
    assert reverse == TEST_GRAPH_REVERSE
    assert roots == [TEST_GRAPH_ROOT]


def test_linearize_graph():
    """Test that the graph linearization produces the correct output."""
    linear = graph.linearise_tree(TEST_GRAPH_REVERSE, TEST_GRAPH_ROOT)
    assert linear == TEST_GRAPH_LINEAR


def test_build_subgraph():
    """Test building the subgraph using a `napari.layers.Tracks` layer as input."""
    data = np.random.random(size=(max(TEST_GRAPH_LINEAR) + 1, 4))
    data[:, 0] = np.arange(data.shape[0])
    data[:, 1] = np.arange(data.shape[0])

    tracks = Tracks(data, graph=TEST_GRAPH)
    root, nodes = graph.build_subgraph(tracks, TEST_GRAPH_ROOT)
    subgraph = [node.ID for node in nodes]

    assert root == TEST_GRAPH_ROOT
    assert subgraph == TEST_GRAPH_LINEAR
