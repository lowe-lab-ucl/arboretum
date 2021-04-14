# Arboretum

### Overview

A dockable widget for [Napari](https://github.com/napari) for tracking cells using [btrack](https://github.com/quantumjot/BayesianTracker).

Features:
+ Integration with btrack to enable localization and cell tracking directly from napari
+ Lineage tree plot widget

[![LineageTree](./examples/napari.png)](http://lowe.cs.ucl.ac.uk/cellx.html)  
*Automated cell tracking and lineage tree reconstruction*.

---  

 :construction:  **WORK IN PROGRESS**  :construction:

 This is actively under development. There will be breaking changes on a daily basis until the first stable release. Use with caution!

 Read more about the scientific project here:
 http://lowe.cs.ucl.ac.uk/cellx.html

---

#### TODO:
+ [ ] Refactor for Napari 0.4.0 (now including `napari.layers.Tracks`!)

---

### Installation

We recommend that you first install Napari. Detailed instructions are here: https://github.com/napari/napari.

```sh
pip install napari[all]
```

then install arboretum:

```sh
git clone https://github.com/quantumjot/arboretum.git
cd arboretum
pip install -e .
```
