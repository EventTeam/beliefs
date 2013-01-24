"""
Defines the Set cells
"""
from beliefs.cells import *

class TypedSetCell(Cell):
    """
    Represents iterable unordered containers.

    A set progresses from maximal uncertainty (when its values can be all
    members of the domain) to a singleton set (when there is only one element
    in the value).  If the set is is overconstrained, values is the empty set
    and no values are possible.
    """
    def __init__(self, domain, iterable=None):
        self.domain = set(domain)
        self.values = None
        if iterable:
            self.values = set()
            for item in iterable:
                if item in self.domain:
                    self.values.add(item)
                else:
                    raise Exception("Value %r not in domain!" % (item,))

    def stem(self):
        """ Spawns a new SetCell of the same domain"""
        return TypedSetCell(self.domain)

    def coerce(self, value):
        """
        Ensures that a value is a TypedSetCell
        """
        if isinstance(value, (TypedSingletonCell, TypedSetCell)):
            return value
        elif hasattr(value, '__iter__'):
            # if the values are consistent with the comparison's domains, then
            # copy them, otherwise, make a new domain with the values.
            if all(map(lambda x: x in self.domain, value)):
                return TypedSetCell(self.domain, value)
            else:
                return TypedSetCell(value, value)
        else:
            if value is None:
                return TypedSetCell(self.domain)
            elif value in self.domain:
                return TypedSetCell(self.domain, [value])
            else:
                return TypedSetCell([value], [value])

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
        return self.same_domain(other) and ((self.values == None and
                other.values == None) or (self.values and \
                        len(self.values.symmetric_difference(other.values)) ==
                        0))

    def is_contradictory(self, other):
        """
        What does it mean for a set to contradict another? If a merge results
        in the empty set -- when both sets are disjoint.

        CONTRADICTION: self = {4} other = {3}
        NOT CONTRADICTION: self = {4} other = {3,4}
        NOT CONTRADICTION: self = {3,4} other = {3}
        """
        other = self.coerce(other)
        return not self.same_domain(other) or \
                (not (self.values is None or other.values is None) \
                        and self.values.isdisjoint(other.values))

    def size(self):
        """
        Returns the member of values for the set
        """
        if self.values is None:
            return len(self.domain)
        else:
            return len(self.values)

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
        if self.values:
            return value in self.values
        else:
            return value in self.domain

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
        if self.values:
            return "{" + ", ".join([ str(v) for v in self.values]) + "}"
        else:
            return "{" + ", ".join([ str(v) for v in self.domain]) + "}"

    def to_dot(self):
        if self.values:
            return ",".join(self.values)
        else:
            return ",".join(self.domain)

    def __hash__(self):
        """
        A set's hash is the aggregate XOR of its children's hashes
        """
        hashval = reduce(lambda x, y: hash(x) ^ hash(y), self.domain, 0)
        if self.values:
            for val in self.values:
                hashval += hash(val)
        if hashval == -2:
            hashval = -1
        return hashval
        
    __contains__ = contains
    __eq__ = is_equal



class TypedSingletonCell(TypedSetCell):
    """
    Wraps a set, but restricts it to a single value
    
    """
    def __init__(self, domain, item=None):
        self.domain = set(domain)
        self.values = None
        if item:
            if item in self.domain:
                self.values = set([item])  # always singleton, but this makes
                # it easy to compare with TypedSetCell
            else:
                raise Exception("Value %r not in domain!" % (item,))

    def stem(self):
        """ Spawns a new SetCell of the same domain"""
        return TypedSingletonCell(self.domain)

    def coerce(self, other):
        """
        Ensures that other is a TypedSingletonCell
        """
        if isinstance(other, TypedSetCell):
            if len(other.values) < 2:
                return other
            else:
                raise CoercionFailure("SingletonCells can only take one value")
        elif isinstance(other, (TypedSetCell,TypedSingletonCell)):
            return other
        else:
            if other in self.domain:
                return TypedSingletonCell(self.domain, other)
            else:
                CoercionFailure("Value '%s' not in the domain", \
                    other)
                    
        assert len(self.values) <= 1, "Singleton violation"

    def is_equal(self, other):
        """
        True iff all members are the same
        """
        if not isinstance(other, (TypedSetCell,TypedSingletonCell)):
            other = self.coerce(other)
        return self.same_domain(other) and self.values == other.values

    def is_contradictory(self, other):
        """
        Contradictions are in any of these cases:
            1. domains differ
            2. self.value defined and not in other.values
        """
        if not isinstance(other, (TypedSetCell,TypedSingletonCell)):
            other = self.coerce(other)
        
        if not self.same_domain(other):
            return True

        if self.values and other.values and other.values.isdisjoint(self.values):
            return True

        return False

    def contains(self, value):
        """ Singleton contains = equality """
        if self.values:
            return value in self.values
        else:
            return value in self.domain
        
    def is_entailed_by(self, other):
        """
        Returns True iff Self is entailed by Other; meaning there is more
        information in other; self is more general; other is more specific.
        """
        if not self.same_domain(other):
            return False

        return (self.values is None) or (other.values and len(other.values) ==
                len(self.values.union(other.values)))

    def size(self):
        """
        Returns 0, 1 or the size of the domain
        """
        if self.values:
            return len(self.values)
        else:
            return len(self.domain)

    def merge(self, other):
        """
        Merges two Singleton Typed Cells.... For two non-disjoint sets, this takes the
        union.
        """
        if not isinstance(other, (TypedSetCell,TypedSingletonCell)):
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
        elif other.size() > 1:
            raise Contradiction("Cannot merge singleton set")
        elif self.is_contradictory(other):
            raise Contradiction("Cannot merge singleton set")
        else:
            if self.values:
                raise Exception("SingletonCell is broke")
                # if we got here, then self.values is not None and somehow
                # other.values contains more information and doesn't contradict
                # it
            self.values = other.values.copy()
            assert len(self.values) <= 1, "Singleton violation"
        return self
    
    __contains__ = contains
    __eq__ = is_equal



if __name__ == '__main__':  

    x = TypedSetCell([1,2,3,4])
    x.merge([2,3])
    x.merge(4)

