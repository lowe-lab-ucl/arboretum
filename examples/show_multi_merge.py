import napari

tracks = [
    [0, 1, 50.5, 7.4],
    [0, 2, 50.3, 59.3],
    [1, 3, 73.2, 100.6],
    [1, 4, 75.2, 150.3],
    [2, 3, 13.1, 110.4],
    [2, 4, 14.8, 150.7],
    [3, 5, 54.4, 200.5],
    [3, 6, 52.1, 250.4],
    [4, 5, 50.5, 7.4],
    [4, 6, 50.3, 59.3],
    [5, 5, 73.2, 100.6],
    [5, 6, 75.2, 150.3],
    [6, 5, 13.1, 110.4],
    [6, 6, 14.8, 150.7],
    [7, 7, 54.4, 200.5],
    [7, 8, 52.1, 250.4],
    [8, 7, 54.4, 200.5],
    [8, 8, 52.1, 250.4],
]
graph = {2: [0], 1: [0], 3: [1], 4: [1], 5: [2], 6: [2], 7: [4, 6], 8: [3, 5]}
# graph = {2: [0], 1:[0], 3:[1], 4:[1], 5:[2], 6:[2], 7:[4, 6], 8:[3, 6]}

viewer = napari.Viewer()
viewer.add_tracks(tracks, graph=graph)
viewer.window.add_plugin_dock_widget(
    plugin_name="napari-arboretum", widget_name="Arboretum"
)

if __name__ == "__main__":
    # The napari event loop needs to be run under here to allow the window
    # to be spawned from a Python script
    napari.run()
