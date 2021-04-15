# Arboretum

## NOTE

:construction:  **DEVELOPMENT PAUSED**  :construction:

We have paused development of arboretum, so this may or may not work with the most recent versions of napari. Use with caution!  However, the Tracks visualisation layer is now officially part of napari.

Read about the API here:
https://napari.org/docs/dev/api/napari.layers.Tracks.html


---

### Overview

A dockable widget for [Napari](https://github.com/napari) for tracking cells using [btrack](https://github.com/quantumjot/BayesianTracker).

Features:
+ Integration with btrack to enable localization and cell tracking directly from napari
+ Lineage tree plot widget

[![LineageTree](./examples/napari.png)](http://lowe.cs.ucl.ac.uk/cellx.html)  
*Automated cell tracking and lineage tree reconstruction*.

---  

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
