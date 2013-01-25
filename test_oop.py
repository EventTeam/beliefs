from beliefs import *

class SpatialObject(DictCell):
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



b = PhysicalObject()
print b
