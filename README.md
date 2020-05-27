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


### Example usage


**NOTE**: We're building the GUI, but if you're keen to try out the tracking and visualizations:

#### Localization, Tracking and Visualization

```python
import napari
import arboretum

from arboretum.utils import localize, track

from skimage import io

# load your segmentation mask
segmentation = io.imread('segmentation.tif')

# set the volume for the tracker, this represents the limits of the observation
# volume. if working in 2D the limits in Z are very large - objects cannot
# enter or leave from above or below the plane. if using 3D data, adjust
# accordingly
tracking_volume = ((0, segmentation.shape[1]),    # xmin, xmax
                   (0, segmentation.shape[2]),    # ymin, ymax
                   (-1e5, 1e5))                   # zmin, zmax

# localize the objects and assign labels
localizations = localize(segmentation)

# now track them (see btrack package for config files)
tracks = track(localizations,
               config_filename='cell_config.json',
               volume=tracking_volume)

# now visualize all of this using napari
with napari.gui_qt():
    viewer = napari.Viewer()

    # visualize the segmentation
    seg_layer = viewer.add_labels(segmentation, name='Segmentation')
    seg_layer.editable = False

    # OPTIONAL: you can visualize the localizations using a points layer
    pts_layer = viewer.add_points(localizations[:,:3], name='Localizations')

    arboretum.build_plugin(viewer, tracks)
```


#### Launching the GUI
```python
import arboretum

# launch the viewer with plugin  
arboretum.run()
```
