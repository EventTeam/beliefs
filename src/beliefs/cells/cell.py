"""
This file defines the atomic and complex cells that are used in Propagator
expressions.

From CSAIL-TR-2009-053: "Instead of thinking of a cell as an object that stores
a value, think of a cell as an object that stores everything you know about a
value..."  Cells accumulate partial information, and meta-data such as provenance.

  - Empty cells are just cells containing no information.
  - "Second values" are more information.
  - Equality tests are tests whether the new information is redundant.
  - Contradiction from different values means the information cannot be
    reconciled.

Propagator Networks are a programming methodology that generalize 'expressions'
to allow values to come from multiple sources.

    Propagator Network: a wiring diagram for information
    Cells: are machines that store data
    Propagators: are machines that interconnect cells

    Merge Procedure:
       * Allows data to be merged to increment information content
        - If equal: do nothing
        - If contradictory: - deal with
        - Set values
       * Track provenance
         - Tolerate global inconsistency
         - Every value has: (1) where it came from, (2) what it depends on

       * Represented as a set of values and premises (dependencies)
        - implies? v1 v2
        - World view:  the set of assumptions that you want to use to
           ?:  How do you pick these? (Minimal set?)

    'amb' operator.
        - *dependency-directed backtracking*
            - evaluating dependencies by recursive descent, you have to
              recompute when you go back
            - every time a failure occurs, it cuts the search space, because of
              the dependency backtracking
            - only recompute things that depend on it
        - if you have a contradiction, you have to know which assumptions it
          depended upon.
        - 'reasons-against', 'reasons-for',
            - if both, then diagnose higher-level assumptions
"""

import copy
import logging
from beliefs.exterior.utils import list_diff
from .exceptions import *

class Cell(object):
    """
    Base class and Interface for Propagator Cells

    Each subclass of Cell must implement:

        * is_equal(other)
            - whether two objects are the same
            - __eq__ = is_equal
        * is_contradictory(other)
        * is_entailed_by(other)
        * merge(other)
            "The fully nuanced question that merge answers is
            ``What do I need to do to the network in order to make
            it reflect the discovery that these two information
            structures are about the same object?''
        * size()
            Describes how large the set is
            - How should we compute sizes for Strings?  Or should
              they return None and we just ignore them?
            - __len__ = size
    Optionally, a static function:
        * coerce(value)

    """
    def __instancecheck__(self, obj):
        """
        defines behavior of isinstance(obj, Cell) that checks to see
        if obj is a Cell
        """
        required_methods = ['is_equal', 'is_contradictory', 'is_entailed_by' \
                'entails', 'merge']
        for method in required_methods:
            if not hasattr(obj, method):
                logging.info("%s is not a cell: missing '%s' method." \
                        % (obj, method))
                return False
        return True
            

    def is_equal(self, other):
        raise NotImplemented 

    def is_contradictory(self, other):
        raise NotImplemented 

    def is_entailed_by(self, other):
        """
        Means that Other is more specific than Self;  Self is more general than
        other.
        """
        logging.error("Needs is_entailed_by in %s" % (str(self)))
        raise NotImplemented
        
    def entails(self, other):
        """
        The inverse of is_entailed_by, meaning Other is more general than Self.
        """
        return other.is_entailed_by(self)

    def merge(self, other):
        """
        Merge has three cases:
            1.  Neither new nor old values are redundant => need both of their
            supports
            2.  If either value is strictly redundant => don't include its
            supports
            3.  If they are equivalent, we can choose which support to take.
              - Use the one already present, unless it has more information

        If two values contradict each other, return a contradiction object.
        (raise a contradiction exception)
        """
        pass
        
    def set(self, other):
        """ Alias for Merge """
        return self.merge(other)

    def __contains__(self, value):
        """
        When primitive cells are checked for containment, it is typically to
        see if it has a particular property
        """
        return False

    def __str__(self):
        """
        Default string representation (deferred to subclass's __repr__)
        """
        return self.__repr__()

    def __deepcopy__(self, memo):
        """
        Copies a Cell but does not copy it's domain or values (extension)
        because these can be recomputed.
        TODO: test that amortized flags (__recompute=False) are not copied
        """
        copied = copy.copy(self)  # shallow copy
        copied.__dict__.update(self.__dict__)
        for key, val in copied.__dict__.items():
            if not key in ['domain', 'values', '_domain_hash']:
                copied.__dict__[key] = copy.deepcopy(val, memo)
        return copied

    def stem(self):
        """ Creates a new instance of the current cell value """
        return self.__class__()

    def cellclass(self):
        """ Returns a string containing the class name """
        return str(self.__class__.__name__)
        
    def __hash__(self):
        """
        A general purpose hash method for cells. If cells have other parts
        that need to be compared, then they need to implement their own.

        This method computes a hash for
            - 'domain' (iterable with hashable elements) 
        and either
               - 'value' (hashable),
            or
               - 'values' (iterable with hashable elements)
        """
        hval = 0

        if hasattr(self, 'domain'):
            # hash the domain 
            if not hasattr(self.__class__, 'domain_hash'):
                # compute domain hash and share among all class members
                print self.__class__
                setattr(self.__class__, 'domain_hash', 
                    reduce(lambda x, y:  hash(x) ^ hash(y), self.domain, 0))
            hval += self.__class__.domain_hash

        if hasattr(self, 'value'):
            # hash the value
            if not self.value:
                return hval
            else:
                hval += hash(self.value)

        elif hasattr(self, 'values'):
            # hash each value in the domain
            if not self.values:
                return hval
            else:
                # works with any iterable value
                hval += reduce(lambda x, y: hash(x) ^ hash(y), self.values, 0)

        else:
            raise CellConstructionFailure("Missing value or values.  Something"\
                    + " wont be __hash__'d correctly in %s" % (self))

        if hval == -2:
            # -2 is a reserved hash value in python.
            hval = -1

        return hval

