 <!--[![Downloads](https://pepy.tech/badge/napari-arboretum)](https://pepy.tech/project/napari-arboretum)-->

[![License](https://img.shields.io/pypi/l/napari-arboretum.svg?color=green)](https://github.com/lowe-lab-ucl/arboretum/blob/main/LICENSE.md)
[![PyPI](https://img.shields.io/pypi/v/napari-arboretum.svg?color=green)](https://pypi.org/project/napari-arboretum)
[![Python Version](https://img.shields.io/pypi/pyversions/napari-arboretum.svg?color=green)](https://python.org)
[![tests](https://github.com/lowe-lab-ucl/arboretum/workflows/tests/badge.svg)](https://github.com/lowe-lab-ucl/arboretum/actions)
[![codecov](https://codecov.io/gh/lowe-lab-ucl/arboretum/branch/main/graph/badge.svg?token=2M2HhM60op)](https://app.codecov.io/gh/lowe-lab-ucl/arboretum/tree/main)

# Arboretum



https://github.com/lowe-lab-ucl/arboretum/assets/8217795/d98c22c4-73bb-493a-9f8f-c224d615209d


_Automated cell tracking and lineage tree reconstruction_.

### Overview

A dockable widget for [Napari](https://github.com/napari/napari) for visualizing cell lineage trees.

Features:

- Lineage tree plot widget
- Integration with [btrack](https://github.com/quantumjot/btrack)

---

### Usage

Once installed, Arboretum will be visible in the `Plugins > Add Dock Widget > napari-arboretum` menu in napari. To visualize a lineage tree, (double) click on one of the tracks in a napari `Tracks` layer.

### Examples

You can use the example script to display some sample tracking data in napari and load the arboretum tree viewer:

```sh
python ./examples/show_sample_data.py
```

Alternatively, you can use _btrack_ to generate tracks from your image data. See the example notebook here:
https://github.com/quantumjot/btrack/blob/main/examples

---

### History

This project has changed considerably. The `Tracks` layer, originally developed for this plugin, is now an official layer type in napari. Read the napari documentation here:
https://napari.org/stable/api/napari.layers.Tracks.html

To view the legacy version of this plugin, visit the legacy branch:
https://github.com/quantumjot/arboretum/tree/v1-legacy
