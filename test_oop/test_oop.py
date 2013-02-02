from beliefs.referent import *

class SpatialObject(Referent):
    """ Represents the properties of an object located in 3D space """
    def __init__(self):
        super(SpatialObject, self).__init__()
        self.x_position = IntervalCell()
        self.y_position = IntervalCell()

class PhysicalObject(SpatialObject):
    """ Represents objects that occupy space"""
    def __init__(self):
        super(PhysicalObject, self).__init__()
        self.height = IntervalCell()
        self.width = IntervalCell()

class Musical(Referent):
    """"""
    def __init__(self):
        super(Musical, self).__init__()
        self.frequency = IntervalCell()


class MusicalThing(PhysicalObject, Musical):
    pass






