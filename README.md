# Arboretum
**WORK IN PROGRESS**  
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

### Example usage

**NOTE**: We're building the GUI, but if you're keen to try out the visualizations:

```python
import napari
import arboretum

from arboretum.utils import localize, track

from skimage import io

# load your segmentation mask
segmentation = io.imread('segmentation.tif')

# use btrack to localize and track these
localizations = localize(segmentation)

# now track them (see btrack package for config files)
tracks = track(localizations, config_filename='cell_config.json')

# now visualize all of this using napari
manager = arboretum.build_manager(tracks)

with napari.gui_qt():
    viewer = napari.Viewer()

    # visuzlize the segmentation
    seg_layer = viewer.add_labels(segmentation, name='Segmentation')
    seg_layer.editable = False

    # OPTIONAL: you can visualize the localizations using a points layer
    pts_layer = viewer.add_points(localizations[:,:3], name='Localizations')

    arboretum.build_plugin(viewer, manager)

```
