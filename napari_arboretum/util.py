from napari.layers import Tracks


class TrackPropertyMixin:
    """
    Mixin class to add ``.tracks`` and ``.track_id`` properties.
    """

    @property
    def tracks(self) -> Tracks:
        """
        napari tracks layer.
        """
        if not hasattr(self, "_tracks"):
            raise AttributeError("No tracks set on this plotter.")
        return self._tracks

    @tracks.setter
    def tracks(self, tracks: Tracks) -> None:
        self._tracks = tracks
        self.on_tracks_change()

    @property
    def track_id(self) -> int:
        """
        napari track ID.
        """
        if not hasattr(self, "_track_id"):
            raise AttributeError("No track ID set on this plotter.")
        return self._track_id

    @track_id.setter
    def track_id(self, track_id: int) -> None:
        self._track_id = track_id
        self.on_track_id_change()

    def on_tracks_change(self) -> None:
        """
        Optional method that derived classes can override to do something
        when the tracks layer changes.
        """

    def on_track_id_change(self) -> None:
        """
        Optional method that derived classes can override to do something
        when the track ID is changed.
        """
