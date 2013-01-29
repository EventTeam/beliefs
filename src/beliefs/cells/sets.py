"""
Defines the Set cells
"""
from beliefs.cells import *

class SetIntersectionCell(Cell):
    """
    Represents iterable unordered elements.
    """
    def __init__(self, domain, value_or_values=None):
        """
        Initializes a SetCell with a domain of `domain` and optionally, a
        list of default values
        """
        self.domain = set(domain)
        self.values = None
        if value_or_values:
            self.values = set()
            for item in value_or_values:
                if item in self.domain:
                    self.values.add(item)
                else:
                    raise Exception("Value %r not in domain!" % (item,))

    @classmethod
    def _stem(clz, *arg):
        """ Creates a new instance of the class with args """
        return clz(*arg)

    def stem(self):
        """ Spawns a new SetCell of the same domain"""
        return self._stem(self.domain)

    def coerce(self, value):
        """
        Ensures that a value is a SetCell
        """
        if hasattr(value, 'values') and hasattr(value, 'domain'):
            return value
        elif hasattr(value, '__iter__'):
            # if the values are consistent with the comparison's domains, then
            # copy them, otherwise, make a new domain with the values.
            if all(map(lambda x: x in self.domain, value)):
                return self._stem(self.domain, value)
            else:
                raise CellConstructionFailure("Cannot turn %s into a cell" % (value))
        elif value in self.domain:
            return self._stem(self.domain, [value])
        else:
            raise CellConstructionFailure("Cannot turn %s into a cell" % (value))

    def same_domain(self, other):
        """
        Cheap pointer comparison or symmetric difference operation
        to ensure domains are the same
        """
        return self.domain == other.domain or \
                len(self.domain.symmetric_difference(set(other.domain))) == 0 
    def is_equal(self, other):
        """
        True iff all members are the same
        """
        other = self.coerce(other)
        return len(self.get_values().symmetric_difference(other.get_values())) == 0

    def is_contradictory(self, other):
        """
        What does it mean for a set to contradict another? If a merge results
        in the empty set -- when both sets are disjoint.

        CONTRADICTION: self = {4} other = {3}
        NOT CONTRADICTION: self = {4} other = {3,4}
        NOT CONTRADICTION: self = {3,4} other = {3}
        """
        other = self.coerce(other)
        # contradictory if both values are disjoint
        return self.get_values().isdisjoint(other.get_values()) 

    def __len__(self):
        """
        Returns the member of values for the set
        """
        return len(self.get_values())

    def is_entailed_by(self, other):
        """
        Fewer members = more information (exception is empty set, which means
        all members of the domain)

         (1) when self is empty and others is not (equal to containing the
          entire domain)
         (2) when other contains more members than self
        
        """
        if not self.same_domain(other):
            return False
        
        if not other.values:
            if self.values:
                # None can never entail -None
                return False
            else:
                # None entails None
                return True
        
        return not self.values or self.values.issuperset(other.values) 

    def contains(self, value):
        """
        Returns True iff value is in the set
        """
        return value in self.get_values()

    def get_values(self):
        """ The main difference between Intersection/Union """
        if self.values:
            return self.values
        else:
            return self.domain

    def merge(self, other):
        """
        We can merge unless the merge results in an empty set -- a
        contradiction
        """
        other = self.coerce(other)
        if self.is_equal(other):
            # pick among dependencies
            return self
        elif other.is_entailed_by(self):
            # other is a subset of self
            return self
        elif self.is_entailed_by(other):
            # self is a subset of other.
            self.values = other.values
        elif self.is_contradictory(other):
            raise Contradiction("Cannot merge set with %s" % (str(other)))
        else:
            # merge mutual information
            if self.values:
                self.values = self.values.intersection(other.values)
            else:
                self.values = other.values.copy()
        return self

    def __repr__(self):
        """ Python-specific representation"""
        return "{" + ", ".join([ str(v) for v in self.get_values()]) + "}"

    def to_dot(self):
        """ For Graphviz rendering """
        return ",".join(self.get_values())

    def __hash__(self):
        """
        A set's hash is the aggregate XOR of its children's hashes
        """
        hashval = 0 
        for val in self.get_values():
            hashval += hash(val)
        if hashval == -2:
            hashval = -1
        return hashval
        
    __contains__ = contains
    __eq__ = is_equal


class SetUnionCell(SetIntersectionCell):
   
    def is_entailed_by(self, other):
        """ Returns True iff self is a proper subset of other """
        sval = self.get_values()
        oval = other.get_values()
        return sval.issubset(oval)

    def merge(self, other):
        """
        We can merge unless the merge results in an empty set -- a
        contradiction
        """
        other = self.coerce(other)
        if self.is_equal(other):
            # pick among dependencies
            return self
        elif other.is_entailed_by(self):
            # other is a subset of self
            return self
        elif self.is_entailed_by(other):
            # self is a subset of other.
            self.values = other.values
        elif self.is_contradictory(other):
            raise Contradiction("Cannot merge set with %s" % (str(other)))
        else:
            # merge mutual information
            if self.values:
                self.values = self.values.union(other.values)
            else:
                self.values = other.values.copy()
        return self


    def get_values(self):
        """ The main difference between Intersection/Union """
        if self.values:
            return self.values
        else:
            return set()


class TypedSetCell(SetIntersectionCell):

    def __init__(self, *args, **kwargs):
        print "TypedSetCell is deprecated. Please use either"
        print " 1) IntersectionCell"
        print " 2) UnionCell"
        SetIntersectionCell.__init__(self, *args, **kwargs)

class TypedSingletonCell(SetIntersectionCell):

    def __init__(self, *args, **kwargs):
        print "TypedSetCell is deprecated. Please use either"
        print " 1) IntersectionCell"
        print " 2) UnionCell"
        SetIntersectionCell.__init__(self, *args, **kwargs)

if __name__ == '__main__':  

    # SetIntersectionCell starts from all possibilities and new options are added
    x = SetIntersectionCell([1,2,3,4])
    assert len(x) == 4
    h1 = hash(x)
    x.merge([2,3])
    assert len(x) == 2
    h2 = hash(x)
    x.merge(2)
    assert len(x) == 1
    h3 = hash(x)
    assert h2 != h3 != h1

    x = SetUnionCell([1,2,3,4])
    print x
    #assert len(x) == 0
    h1 = hash(x)
    x.merge([2,3])
    assert len(x) == 2
    h2 = hash(x)
    x.merge(2)
    assert len(x) == 2
    h3 = hash(x)
    assert h2 == h3
    assert h1 != h2

    x = SetUnionCell([1,2,3,4], [2])
    assert len(x) == 1
    x.merge([2,3,4])
    assert len(x) == 3
    x.merge([2])
    assert len(x) == 3
    x.merge([2])
    assert len(x) == 3
