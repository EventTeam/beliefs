from cell import *
import logging

class SetIntersectionCell(Cell):
    """
    Represents iterable unordered elements.

    :param domain: Initial domain
    :type domain: iterable
    :param value_or_values: Optional default values. All values must be in the specified domain.
    :type value_or_values: list
    :raises: Exception
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
        """
        Spawns a new SetCell of the same domain

        :returns: SetIntersectionCell

        >>> a = SetIntersectionCell([1,2,3])
        >>> b = a.stem()
        >>> b
        {1,2,3}

        """
        return self._stem(self.domain)

    def coerce(self, value):
        """
        Ensures that a value is a SetCell

        :param value: A Cell or value in ``self``'s domain
        :returns: SetIntersectionCell
        :raises: CellConstructionFailure

        >>> a = SetIntersectionCell([1,2,3])
        >>> b = a.coerce([1,2])
        >>> b
        {1,2}
        >>> c = a.coerce(1)
        >>> c
        {1}
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

        :param other: SetCell to be compared
        :type other: SetCell
        :returns: bool

        >>> a = SetIntersectionCell([1,2,3])
        >>> b = SetIntersectionCell([2,3,1])
        >>> c = SetIntersectionCell([1,2])
        >>> a.same_domain(b)
        True
        >>> a.same_domain(c)
        False
        """
        return self.domain == other.domain or \
                len(self.domain.symmetric_difference(set(other.domain))) == 0 
    def is_equal(self, other):
        """
        True iff all members are the same

        :param other: SetCell to be compared
        :type other: SetCell
        :returns: bool
        :raises: CellConstructionFailure

        >>> a = SetIntersectionCell(range(10))
        >>> b = SetIntersectionCell(range(10),[1,3,5])
        >>> c = SetIntersectionCell([1,3,5])
        >>> a.is_equal(b)
        False
        >>> b.is_equal(c)
        True
        """
        other = self.coerce(other)
        return len(self.get_values().symmetric_difference(other.get_values())) == 0

    def is_contradictory(self, other):
        """
        What does it mean for one set to contradict another? Two sets are contradictory when they are disjoint.

        :param other: A SetCell to be compared
        :type other: SetCell
        :returns: bool
        :raises: CellConstructionFailure

        >>> a = SetIntersectionCell(['a','b','c'])
        >>> b = SetIntersectionCell(['d','e','f'])
        >>> c = SetIntersectionCell(['c','d'])
        >>> a.is_contradictory(b)
        True
        >>> a.is_contradictory(c)
        False
        >>> b.is_contradictory(c)
        False
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

        If the two SetCells do not have the same domain, this method returns ``False``.

        If the two SetCells have the same domain, then *self* is entailed by *other* if ``self.values`` is a subset of ``other.values``, or if ``other.values`` is empty (``None``).


         :param other: A SetCell to be tested
         :type other: SetCell
         :returns: bool

        >>> a = SetIntersectionCell(range(10),[1,2,3])
        >>> b = SetIntersectionCell(range(5),[1,2,3])
        >>> c = SetIntersectionCell(range(10),[1,2])
        >>> a.is_entailed_by(b)
        False
        >>> a.is_entailed_by(c)
        True
        >>> c.is_entailed_by(a)
        False
        
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

        :param other: A value that may or may not be in the domain of *self*.
        :returns: bool

        >>> a = SetIntersectionCell(['red','blue','green'],['red','blue'])
        >>> b = SetIntersectionCell(['red','blue','green'])
        >>> a.contains('red')
        True
        >>> a.contains('green')
        False
        >>> b.contains('green')
        True
        """
        return value in self.get_values()

    def get_values(self):
        """ Returns the values of the set, or the domain as a set if no values were specified at construction.

        :returns: set

        >>> x = SetIntersectionCell(['a','b','c'])
        >>> y = SetIntersectionCell(['a','b','c'],['a','b'])
        >>> x.get_values()
        set(['a', 'c', 'b'])
        >>> y.get_values()
        set(['a', 'b'])
        """
        if self.values:
            return self.values
        else:
            return self.domain

    def merge(self, other):
        """
        We can merge unless the merge results in an empty set -- a
        contradiction. This method results in the intersection of the two SetCells.

        .. note::
            This method modifies the *self* argument.

        :param other: SetCell to merge with
        :type other: SetCell
        :returns: SetCell
        :raises: Contradiction, CellConstructionFailure

        >>> a = SetIntersectionCell(range(10),range(10))
        >>> b = SetIntersectionCell(range(10),[1,2,3])
        >>> a.merge(b)
        {1,2,3}
        >>> c = SetIntersectionCell(range(7),[2,3,4])
        >>> a.merge(c)
        {2,3}
        
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
            self.values = other.values.copy()
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
    to_latex = to_dot


class SetUnionCell(SetIntersectionCell):
    """ SetUnionCell inherits from SetIntersectionCell and breaks monotonicity.
    Initially, its values are equal to its domain, and then after 1 or more updates, its values become the UNION of all of the updates"""

    def merge(self, other):
        """
        We can merge unless the two sets are contradictory, i.e. they are disjoint. The resulting merge will be the union of the two sets.

        .. note::
            This method will modify the *self* argument.

        :param other: SetCell to merge with
        :type other: SetCell
        :returns: SetCell
        :raises: Contradiction, CellConstructionFailure

        >>> a = SetUnionionCell(range(10),range(5))
        >>> b = SetUnionionCell(range(10),range(3,8))
        >>> a.merge(b)
        {0,1,2,3,4,5,6,7,8}
        
        """
        other = self.coerce(other)
        if self.is_equal(other):
            # pick among dependencies
            return self
        elif self.is_contradictory(other):
            raise Contradiction("Cannot merge set with %s" % (str(other)))
        else:
            # self may be a subset of other 
            # or other may be a subset of self
            # merge mutual information
            if self.values:
                self.values = self.values.union(other.values)
            else:
                self.values = other.values.copy()
        return self


class TypedSetCell(SetIntersectionCell):

    def __init__(self, *args, **kwargs):
        logging.info("TypedSetCell is deprecated. Please use either" +
                "1) IntersectionCell or 2) UnionCell")
        SetIntersectionCell.__init__(self, *args, **kwargs)

class TypedSingletonCell(SetIntersectionCell):

    def __init__(self, *args, **kwargs):
        logging.info("TypedSingletonCell is deprecated. Please use either" +\
                "1) IntersectionCell or 2) UnionCell")
        SetIntersectionCell.__init__(self, *args, **kwargs)

if __name__ == '__main__':  

    # SetIntersectionCell starts from all possibilities and new options are added
    two = SetIntersectionCell([1,2,3,4])
    two.merge(2)
    three = SetIntersectionCell([1,2,3,4])
    three.merge(3)
    four = SetIntersectionCell([1,2,3,4])
    four.merge(4)

    x = SetIntersectionCell([1,2,3,4])
    assert x.is_entailed_by(two)
    assert len(x) == 4
    h1 = hash(x)
    x.merge([2,3])
    assert x.is_entailed_by(two)
    assert x.is_entailed_by(three)
    assert not x.is_entailed_by(four)
    assert not x.entails(two)
    assert not x.entails(three)
    assert not x.entails(four)
    assert len(x) == 2
    h2 = hash(x)
    x.merge(2)
    assert not 1 in x
    assert 2 in x
    assert not 3 in x
    assert not 4 in x
    assert not 5 in x
    assert x.entails(two)
    assert two.entails(x)
    assert x.is_entailed_by(two)
    assert two.is_entailed_by(x)
    assert not x.entails(three)
    assert not x.entails(four)
    assert len(x) == 1
    h3 = hash(x)
    assert h2 != h3 != h1

    x = SetUnionCell([1,2,3,4])
    assert 1 in x
    assert 2 in x
    assert 3 in x
    assert 4 in x
    assert len(x) == 4
    h1 = hash(x)
    x.merge([2,3])
    print x
    assert 2 in x
    assert 3 in x
    assert len(x) == 2
    h2 = hash(x)
    x.merge(2)
    print x
    assert len(x) == 2
    h3 = hash(x)
    assert h2 == h3
    assert h1 != h2

    x = SetUnionCell([1,2,3,4], [2])
    h0 = hash(x)
    assert len(x) == 1
    x.merge([2,3,4])
    h1 = hash(x)
    assert h1 != h0
    assert len(x) == 3
    x.merge([2])
    assert len(x) == 3
    x.merge([2])
    assert len(x) == 3
