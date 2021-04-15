import btrack
import napari

from arboretum import build_plugin

objects = btrack.dataio.import_JSON("./objects.json")
config = btrack.utils.load_config("./cell_config.json")

# track the objects
with btrack.BayesianTracker() as tracker:

    # configure the tracker using a config file, append objects and set vol
    tracker.configure(config)
    tracker.append(objects)
    tracker.volume = ((0, 1200), (0, 1600), (-1e5, 1e5))

    # track them and (optionally) optimize
    tracker.track_interactive(step_size=100)
    tracker.optimize()

    # get the tracks, properties and graph
    data, properties, graph = tracker.to_napari(ndim=2)

with napari.gui_qt():
    viewer = napari.Viewer()
    viewer.add_tracks(
        data, properties=properties, graph=graph, name="tracks", blending="translucent"
    )

    widget = build_plugin(viewer)
    viewer.window.add_dock_widget(widget, area="right", name="arboretum")
