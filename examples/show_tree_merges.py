import napari
import numpy as np


def _circle(r, theta):
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    return x, y


def tracks_3d_merge_split():
    """Create tracks with splitting and merging."""

    timestamps = np.arange(500)

    def _trajectory(t, r, track_id):
        theta = t * 0.1
        x, y = _circle(r, theta)
        z = t  # np.zeros(x.shape)
        tid = np.ones(x.shape) * track_id
        return np.stack([tid, t, z, y, x], axis=1)

    track_a = _trajectory(timestamps[:100], 30.0, 0)
    track_b = _trajectory(timestamps[100:400], 10.0, 1)
    track_c = _trajectory(timestamps[100:200], 50.0, 2)
    track_d = _trajectory(timestamps[200:500], 40.0, 3)
    track_e = _trajectory(timestamps[200:400], 60.0, 4)
    track_f = _trajectory(timestamps[400:500], 30.0, 5)

    data = [track_a, track_b, track_c, track_d, track_e, track_f]
    tracks = np.concatenate(data, axis=0)
    tracks[:, 2:] += 50.0  # centre the track at (50, 50, 50)

    # graph = {1: 0, 2: [0], 3: [1, 2]}
    graph = {1: [0], 2: [0], 3: [2], 4: [2], 5: [4, 1]}

    features = {"time": tracks[:, 1]}

    return tracks, features, graph


tracks, features, graph = tracks_3d_merge_split()


viewer = napari.Viewer()
viewer.add_tracks(tracks, features=features, graph=graph)
viewer.window.add_plugin_dock_widget(
    plugin_name="napari-arboretum", widget_name="Arboretum"
)

if __name__ == "__main__":
    # The napari event loop needs to be run under here to allow the window
    # to be spawned from a Python script
    napari.run()
