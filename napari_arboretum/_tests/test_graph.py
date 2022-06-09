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
    nodes = graph.build_subgraph(tracks, TEST_GRAPH_ROOT)
    subgraph = [node.ID for node in nodes]

    assert subgraph == TEST_GRAPH_LINEAR


def test_get_root():
    """Test getting the graph root."""
    data = np.random.random(size=(max(TEST_GRAPH_LINEAR) + 1, 4))
    data[:, 0] = np.arange(data.shape[0])
    data[:, 1] = np.arange(data.shape[0])

    tracks = Tracks(data, graph=TEST_GRAPH)
    root_id = graph.get_root_id(tracks, TEST_GRAPH_ROOT)
    assert root_id == TEST_GRAPH_ROOT


def test_node_is_root():
    """Test the `TreeNode` class."""
    node = graph.TreeNode(generation=1, ID=1, t=(1, 2))
    assert node.is_root

    node = graph.TreeNode(generation=2, ID=1, t=(1, 2))
    assert not node.is_root


def test_node_is_leaf():
    """Test the `TreeNode` class."""
    node2 = graph.TreeNode(generation=2, ID=2, t=(2, 3))
    node1 = graph.TreeNode(generation=1, ID=1, t=(1, 2), children=[node2])
    assert not node1.is_leaf
    assert node2.is_leaf


def test_add_child():
    node = graph.TreeNode(generation=1, ID=1, t=(1, 2))
    assert node.is_leaf
    child = node.add_child(2, t_end=4)

    assert not node.is_leaf
    assert len(node.children) == 1

    assert child.is_leaf
    assert child.t == (2, 4)
