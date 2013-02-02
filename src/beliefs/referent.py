"""  This file defines two classes, TaxonomyCell and Referent, which work in 
tandem to provide the 'kind' property to all referents, and the generalization
structure.  The generalization structure (a taxonomy-- a directed acyclic graph
of IS-A relationships) is automatically constructed using the object-oriented
inheritance structures of classes that inherit from Referents.

Referent is a sub-class of DictCell and contains an instance of TaxonomyCell, which
is initialized to the base class of whatever subclasses Referent.

In the file that loads all Referent subclasses, usually __init__.py, after all
classes are loaded, there must be a special call to initialize TaxonomyCell's 
domain:

    >> import sys
    >> from beliefs.referent import *
    >>
    >> TaxonomyCell.initialize(sys.modules[__name__])

"""
import inspect
import networkx as nx
from beliefs.cells import *

class TaxonomyCell(PartialOrderedCell):
    """ A taxonomy of all DictCell subclasses."""

    def __init__(self, initial_value=None):
        if not self.has_domain(): # only initialize once
            raise Exception("TaxonomyCell.initialize(sys.modules[__name__]) must be called after importing classes")
            print "initializing"
            # represents IS-A relationships

        PartialOrderedCell.__init__(self, None)
        
        if initial_value:
            self.merge(initial_value)

    @classmethod
    def initialize(clz, modules):
        taxonomy = TaxonomyCell.build_class_graph(modules)
        clz.set_domain(taxonomy)
        
    @staticmethod
    def build_class_graph(modules, klass=None, graph=None):
        """ Builds up a graph of the DictCell subclass structure """
        if klass is None:
            class_graph = nx.DiGraph()
            for name, classmember in inspect.getmembers(modules, inspect.isclass):
                if issubclass(classmember, Referent) and classmember is not Referent:
                    TaxonomyCell.build_class_graph(modules, classmember, class_graph)
            return class_graph
        else:
            parents = getattr(klass, '__bases__')
            for parent in parents:
                if parent != Referent:
                    graph.add_edge(parent.__name__, klass.__name__)
                    # store pointer to classes in property 'class'
                    graph.node[parent.__name__]['class'] = parent
                    graph.node[klass.__name__]['class'] = klass 
                    if issubclass(parent, Referent):
                        TaxonomyCell.build_class_graph(modules, parent, graph)



class Referent(DictCell):
    """ Thin DictCell subclass to inject the TaxonomyCell property after 
    initialization """

    def __init__(self, *args, **kwargs):
        DictCell.__init__(self, *args, **kwargs)
        self.kind = TaxonomyCell(self.__class__.__name__)

    @classmethod
    def from_json(clz, jsonobj):
        """ Creates a referent instance of type `json.kind` and 
        initializes it to default values.
        """
        # convert strings to dicts
        if isinstance(jsonobj, (str, unicode)):
            jsonobj = json.loads(jsonobj)
        
        assert 'cells' in jsonobj, "No cells in object"
       
        domain = clz.get_domain()
        cells = []
        for cell_dna in jsonobj['cells']:
            assert 'kind' in cell_dna, "No type definition"
            classgenerator = domain.node[cell_dna['kind']]['class']
            cell = classgenerator()
            for attr, val in cell_dna.items():
                if not attr in ['kind']:
                    cell[attr].merge(val)
                    cells.append(cell)

        return cells


