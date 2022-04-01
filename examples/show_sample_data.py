"""
Load and show sample data
=========================
This example:
- loads some sample data
- adds the data to a napari viewer
- loads the arboretum plugin
- opens the napari viewer
"""
import napari

from napari_arboretum import load_sample_data

track, segmentation = load_sample_data()

viewer = napari.Viewer()
viewer.add_layer(segmentation)
viewer.add_layer(track)
viewer.window.add_plugin_dock_widget(
    plugin_name="napari-arboretum", widget_name="Arboretum"
)

if __name__ == '__main__':
    # The napari event loop needs to be run under here to allow the window
    # to be spawned from a Python script
    napari.run()
