"""
Imports Cell datastructures for merging and dealing with partial information.
"""

__version__ = "0.1"

from cell import Cell
from bools import *
from numeric import *
from setCells import *
from lists import *
from strings import *
from posets import *
from dicts import *
from exceptions import *

# special cells
from colors import *
from spatial import *
from lazy import *

import networkx as nx

import networkx as nx

class LexicaTaxonomyCell(PartialOrderedCell):
    """ A type system for lexica """

    def __init__(self, initial_value=None):
        """
        Initializes a graph containing the partial ordering of TV show
        genre names.
        """
        genre_dag = None
        if not self.has_domain(): # only initialize once
            genre_dag = nx.DiGraph()
            # represents IS-A relationships

            genre_dag.add_edge("entity", "thing")
            genre_dag.add_edge("entity", "event")
            genre_dag.add_edge("event", "action")
            genre_dag.add_edge("thing", "kindle")
            genre_dag.add_edge("thing", "shape")
            genre_dag.add_edge("shape", "shape_with_tail")
            genre_dag.add_edge("shape", "shape_without_tail")
            genre_dag.add_edge("event", "media")
            genre_dag.add_edge("media", "tv_show")
            genre_dag.add_edge("media", "movie")
            
        PartialOrderedCell.__init__(self, genre_dag)
        
        if initial_value:
            self.merge(initial_value)
            
            
