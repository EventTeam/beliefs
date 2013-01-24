import numpy as np
import json

#from stategraph.cells import *
from .dicts import *
from .cell import *

class LazyCell(Cell):
    """
    This is a proxy for accessing (partially enumerated) sets of candidate
    cells.  LazyCells are constrained to be within the value of their prototype

    Question:
        How to handle dynamic properties?
          - When we update_intension(), the members that are saved will be
            filtered against the criteria of the prototype. Should we save ALL
            properties on Yahoo search, or just the ones that
        How to handle when a property has changed?
    """
    def __init__(self, prototype):
        """
         - Memoize should be 'True' when the update_intension function
           accesses a remote API or the number of elements being generated is
           very small.
        """
        # we need this dict notation in the __init__ b/c the __setattr__ is
        # overloaded
        self.__dict__['prototype'] = prototype
        self.__dict__['members'] = {}
        # define constraints
        if not isinstance(prototype, DictCell):
            raise Exception("Error: prototype must be a DictCell")

        self.__dict__['filters'] = []
        self.__dict__['orderings'] = []

        self.__dict__['include'] = {}  # additional members (hash -> members)
        self.__dict__['exclude'] = set()  # hash ids to exclude

        # broker object parameters
        self.__dict__['_size_full_intension'] = np.inf
        self.__dict__['_size_known_intension'] = 0
        self.__dict__['_update_members'] = True

    def size(self):
        """
        Size of LazyCell:  the size of the intension plus accounting for
        excluded and included additions.

        The exclusions are assumed to be part of the set
        The inclusions are assumed to NOT be part of the intension
        """
        return self._size_full_intension \
                    - len(self.exclude)\
                    + len(self.include)

    def update(self):
        """
        Updates intension and then adds or includes extension
        """
        # updates intension
        self.update_intension()
        self._size_known_intension = len(self.members)
        self._update_members = False

    def update_intension(self):
        """
        Subclass specific method for generating self.members
        The methods responsibilities are:

         - Defining self.members: mapping hash(m) -> m
         - Defining self._size_full_intension
        """
        raise NotImplemented("Each LazyCell must have an update_intension" +
                " method.  Missing in %s" % self.__class__.__name__)

    def is_entailed_by(self, other):
        """
        Means merging other with self does not produce any new information.
        """
        if not set(self.include.keys()).issubset(set(other.include.keys())):
            return False
        if not self.exclude.isuperset(other.exclude):
            return False
        if not self.prototype.is_entailed_by(other.prototype):
            return False
        return True
    
    def is_equal(self, other):
        """
        The objects must be the same
          - Same members (if enumerated)
          - Or same structure (if not enumerated)

        If the merge does not produce any new information (or contradiction)
        then these are equal.
        """
        print type(self.prototype), type(other.prototype)
        if not self.prototype.is_equal(other.prototype):
            print "Different prototypes"
            return False
        if self.exclude != other.exclude:
            print "Different excludes"
            return False
        if self.include != other.include:
            print "Different includes"
            return False
        return True
            
    def get_instances(self):
        """
        Returns the members of the LazyDict
        """
        if self._update_members: self.update()
        return iter(sorted(self.members.iteritems()))

    def is_contradiction(self, other):
        """
        Is contradiction means that a merge of the new information with the
        LazyCell will result in 0 members and is over constrained.
        """
        raise NotImplemented

    def merge(self, other):
        """
        There can be several types of values for other
            - A parameter that is responsible for generating the instances
            - A constraint that filters the possible values of the instances
            - A (negated) instance of the class
        """
        raise NotImplemented

    def __getattr__(self, key):
        """
        Get via . operator
        """
        if not hasattr(self, 'prototype'):
            # to make pickle work
            raise AttributeError("No property attribute 'prototype'")
        if key in self.prototype:
            return self.prototype[key]
        elif hasattr(self, key):
            return object.__getattr__(self, key)
        else: 
            raise AttributeError("No attribute '%s'" % (key,))

    def __setattr__(self, key, val):
        """
        Set via . operator
        """
        if key in self.prototype:
            self.prototype[key] = val
            self._update_members = True
            # TODO: we could be more efficient about this and only
            # _update_members if values are actually changed
        else:
            object.__setattr__(self, key, val)

    def __iter__(self):
        for x,y in self.prototype:
            yield x,y

    def __contains__(self, key):
        return key in self.prototype

    def __repr__(self):
        """
        String representation
        """
        s = "LazyCell: %i\n" % (id(self))
        s += "\t prototype:\n" 
        s += str(self.prototype)
        return s

    def __hash__(self):
        """ Extend Cell's hash method to include excludes/includes"""
        hash_val = hash(self.prototype)
        hash_val += reduce(lambda x, y: hash(x) ^ hash(y), self.exclude, 0)
        hash_val += reduce(lambda x, y: hash(x) ^ hash(y), self.include, 0)
        return hash_val
        
    __eq__ = is_equal
    
    
