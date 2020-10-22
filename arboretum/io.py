import btrack


class TrackerFrozenState:
    """ Capture the Tracker state at the end of tracking """

    def __init__(self):
        self.objects = None
        self.tracks = None
        self.lbep = None
        self.refs = None
        self.dummies = None

    def set(self, tracker: btrack.BayesianTracker):
        for key in self.__dict__.keys():
            setattr(self, key, getattr(tracker, key))
