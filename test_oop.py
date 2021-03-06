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

class Musical(DictCell):
    """"""
    def __init__(self):
        super(Musical, self).__init__()
        self.frequency = IntervalCell()


class MusicalThing(PhysicalObject, Musical):
    pass



import sys
import inspect
import networkx as nx


def build_class_graph(klass=None, graph=None):
    if klass is None:
        class_graph = nx.DiGraph()
        for classmember in inspect.getmembers(sys.modules[__name__], inspect.isclass):
            print classmember
            build_class_graph(classmember, class_graph)
    parents = getattr(klass, '__bases__')
    for parent in parents:
        if parent != DictCell:
            print parent, "->", klass
            graph.add_edge(parent, klass)
            build_class_graph(parent, graph)



