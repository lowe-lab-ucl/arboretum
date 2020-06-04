# Arboretum
:construction:  **WORK IN PROGRESS**  :construction:

http://lowe.cs.ucl.ac.uk/cellx.html

Dockable widget for [Napari](https://github.com/napari) for visualizing cell track data.

Features:
+ Custom `Track` layer for fast visualization of track data in napari
+ Integration with bTrack to enable localization and cell tracking from napari
+ Lineage tree plot widget
+ Track count widget

[![LineageTree](./examples/track_layer.jpeg)](http://lowe.cs.ucl.ac.uk/cellx.html)  
*Automated cell tracking and lineage tree reconstruction*.

**See [bTrack](https://github.com/quantumjot/BayesianTracker) page for more
 information about the cell tracking library.**


---

TODO:
+ [ ] pip installer
+ [x] GUI for bTrack localization and tracking directly from Napari
+ [x] 3D track visualization (2D+t -> 3D, and 3D+t)
+ [ ] Mouse interaction with tracks, click to select etc...
+ [x] Mouse cursor returns nearest track ID
+ [x] Store localizations in points layer, allowing interactive track editing
+ [x] Migrate to unified track data model
+ [x] Track coloring by track properties
+ [x] Visualize track merging or branching using a 'graph'
+ [ ] Proper slicing when working in nd space


---

### Installation

```sh
$ git clone https://github.com/quantumjot/arboretum.git
$ cd arboretum
$ pip install -e .
```


### Testing the installation

Following installation, you can test the `Track` layer, as well as the *btrack*
package by running a built-in test. The test downloads some example data and a
tracker configuration file, tracks the objects and then renders the tracks with
*Napari*:

```sh
$ cd tests
$ python test.py
```

### Example usage

**NOTE** You need to provide your own segmentation. There are lots of exciting
methods for this, depending on your data. Assuming you have a tif stack with
your segmentation, you can launch the tracking and visualization plugin like
this:

```python
import arboretum

from skimage import io
seg = io.imread('path/to/your/segmentation.tif') # should be 8-bit

# launch the viewer with plugin  
arboretum.run(segmentation=seg)
```

At the moment there are a few buttons:
+ Load (load HDF or JSON files created by btrack)
+ Configure (load a btrack configuration file)
+ Localize (find objects using the segmentation layer)
+ Track (track the localized objects)
+ Save (save the data - not currently operational)

### State labelling

You can improve the quality of the tracking by providing cell 'states' along
with the segmentation. The plugin uses the following labels for the segmentation:

1. Unlabelled/Interphase
2. Pro(meta)phase
3. Metaphase/Pre-mitosis
4. Anaphase/Post-mitosis
5. Dead/Apoptosis

Change the labels on the segmentation using the labels tool, or provide a
pre-labelled segmentation.
