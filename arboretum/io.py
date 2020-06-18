import numpy as np
import btrack



class TrackerFrozenState:
    """ Capture the Tracker state at the end of tracking """
    def __init__(self):
        self.objects = None
        self.tracks = None
        self.lbep = None
        self.refs = None
        self.dummies = None

    def set(self, tracker):
        for key in self.__dict__.keys():
            setattr(self, key, getattr(tracker, key))



class ArboretumHDFHandler(btrack.dataio.HDF5FileHandler):
    """ ArboretumHDFHandler

    Extend the default btrack HDF handler to deal with writing out segmentation,
    objects and tracks

    Generic HDF5 file hander for reading and writing datasets. This is
    inter-operable between segmentation, tracking and analysis code.

    LBEPR is a modification of the LBEP format to also include the root node
    of the tree.

        I - number of objects
        J - number of frames
        K - number of tracks

    Added generic filtering to object retrieval, e.g.
        obj = handler.filtered_objects('flag==1')
        retrieves all objects if there is an object['flag'] == 1

    Basic format of the HDF file is:
        segmentation/
            images          - (J x h x w) uint8 images of the segmentation
        objects/
            obj_type_1/
                coords      - (I x 5) [t, x, y, z, object_type]
                labels      - (I x D) [label, (softmax scores ...)]
                map         - (J x 2) [start_index, end_index] -> coords array
            ...
        tracks/
            obj_type_1/
                tracks      - (I x 1) [index into coords]
                dummies     - similar to coords, but for dummy objects
                map         - (K x 2) [start_index, end_index] -> tracks array
                LBEPR       - (K x 5) [L, B, E, P, R, G]
                fates       - (K x n) [fate_from_tracker, ...future_expansion]
            ...

    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    @brack.dataio.h5check_property_exists('segmentation')
    def segmentation(self):
        return self._hdf['segmentation']['images'][:].astype(np.uint8)

    def write_segmentation(self,
                           segmentation: np.ndarray,
                           obj_type='obj_type_1'):

        """ write out the segmentation to an HDF file """

        # write the segmentation out
        grp = self._hdf.create_group('segmentation')
        # grp.create_dataset(f'images_{obj_type}',
        grp.create_dataset(f'images',
                           data=segmentation,
                           dtype='uint8',
                           compression='gzip',
                           compression_opts=7)

    def write_objects(self,
                      tracker_state: TrackerFrozenState,
                      obj_type='obj_type_1'):

        #TODO(arl): make sure that the objects are ordered in time

        self._hdf.create_group('objects')
        grp = self._hdf['objects'].create_group(obj_type)

        n_objects = len(tracker_state.objects)
        n_frames = np.max([o.t for o in tracker_state.objects]) + 1

        txyz = np.zeros((n_objects, 5), dtype=np.float32)
        labels = np.zeros((n_objects, 1), dtype=np.uint8)
        fmap = np.zeros((n_frames, 2), dtype=np.uint32)

        # convert the btrack objects into a numpy array
        for i, obj in enumerate(tracker_state.objects):
            txyz[i,:] = [obj.t, obj.x, obj.y, obj.z, 1]
            labels[i,:] = obj.label

            # update the frame map
            t = int(obj.t)
            fmap[t, 1] = np.max([fmap[t, 1], i])

        fmap[1:,0] = fmap[:-1,1]

        grp.create_dataset('coords', data=txyz, dtype='float32')
        grp.create_dataset('labels', data=labels, dtype='float32')
        grp.create_dataset('map', data=fmap, dtype='uint32')
