# Arboretum
:construction:  **WORK IN PROGRESS**  :construction:

http://lowe.cs.ucl.ac.uk/cellx.html

Dockable widget for [Napari](https://github.com/napari) for visualizing cell track data.

Features:
+ Custom `Track` layer for fast visualization of track data in Napari
+ Lineage tree plot widget
+ Track count widget
+ Integration with bTrack

[![LineageTree](./examples/napari.png)](http://lowe.cs.ucl.ac.uk/cellx.html)  
*Automated cell tracking and lineage tree reconstruction*.

**See [bTrack](https://github.com/quantumjot/BayesianTracker) page for more information about the cell tracking**


---

TODO:
+ [ ] pip installer
+ [ ] GUI for bTrack localization and tracking directly from Napari
+ [ ] 3D track visualization (2D+t -> 3D, and 3D+t)
+ [ ] Mouse interaction with tracks


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

At the moment there are 4 (four!) buttons:
+ Load (load HDF or JSON files created by btrack)
+ Localize (find objects using the segmentation layer)
+ Track (track the localized objects)
+ Save (save the data - not currently operational)
