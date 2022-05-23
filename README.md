 <!--[![Downloads](https://pepy.tech/badge/napari-arboretum)](https://pepy.tech/project/napari-arboretum)-->
[![License](https://img.shields.io/pypi/l/napari-arboretum.svg?color=green)](https://github.com/lowe-lab-ucl/napari-arboretum/raw/master/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/napari-arboretum.svg?color=green)](https://pypi.org/project/napari-arboretum)
[![Python Version](https://img.shields.io/pypi/pyversions/napari-arboretum.svg?color=green)](https://python.org)
[![tests](https://github.com/lowe-lab-ucl/arboretum/workflows/tests/badge.svg)](https://github.com/quantumjot/arboretum/actions)
[![codecov](https://codecov.io/gh/lowe-lab-ucl/arboretum/branch/master/graph/badge.svg?token=2M2HhM60op)](https://codecov.io/gh/lowe-lab-ucl/arboretum)

# Arboretum


![](https://raw.githubusercontent.com/lowe-lab-ucl/arboretum/master/examples/arboretum.gif)
*Automated cell tracking and lineage tree reconstruction*.

### Overview

A dockable widget for [Napari](https://github.com/napari) for visualizing cell lineage trees.

Features:
+ Lineage tree plot widget
+ Integration with [btrack](https://github.com/quantumjot/BayesianTracker)

---

### Usage

Once installed, Arboretum will be visible in the `Plugins > Add Dock Widget > napari-arboretum` menu in napari.  To visualize a lineage tree, click on one of the tracks in a napari `Tracks` layer.



### Examples

You can use the example script to display some sample tracking data in napari and load the arboretum tree viewer:

```sh
python ./examples/show_sample_data.py
```

Alternatively, you can use *btrack* to generate tracks from your image data. See the example notebook here:
https://github.com/quantumjot/BayesianTracker/blob/master/examples

---

### History

This project has changed considerably. The `Tracks` layer, originally developed for this plugin, is now an official layer type in napari. Read the napari documentation here:
 https://napari.org/api/napari.layers.Tracks.html


To view the legacy version of this plugin, visit the legacy branch:
https://github.com/quantumjot/arboretum/tree/v1-legacy
