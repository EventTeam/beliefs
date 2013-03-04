from cell import *

class LinearOrderedCell(Cell):
    """
    A generalization of IntervalCell to non-numeric symbols
    """
    def __init__(self, ordered_domain, low=None, high=None):
        """
        Parameters:
          - ordered_domain:  an ordered sequence of symbols
          - low: a symbol in the domain that marks the lower bound
          - high: a symbol in the domain that marks the upper bound
        """
        if not isinstance(ordered_domain, list):
            raise CellConstructionFailure("Ordered domain must be a list, with fixed order")
        if len(ordered_domain) != len(set(ordered_domain)):
            # duplicate entries
            raise CellConstructionFailure("All elements of the domain need unique hash")

        self.domain = ordered_domain
        self.low = low
        self.high = high

        # sanity checks
        if low is None:
            self.low = self.domain[0]
        elif low not in self.domain: 
            raise CellConstructionFailure("Value low='%s' not in domain." \
              % (low))
        
        if high is None:
            self.high = self.domain[-1]
        elif high not in self.domain:
            raise CellConstructionFailure("Value high='%s' not in domain." \
                        % (high))

        assert self.domain.index(self.low) <= self.domain.index(self.high), \
                "Lower bound must be <= upper "

    def stem(self):
        """ Creates a new instance without any values """
        return self.__class__(self.domain)

    def coerce(self, value):
        """
        Takes one or two values in the domain and returns a LinearOrderedCell
        with the same domain

        :param value: A single value in the domain, or a 2-element list or tuple of values in the domain
        :returns: LinearOrderedCell
        :raises: Exception
        """
        if isinstance(value, LinearOrderedCell) and (self.domain == value.domain or \
            list_diff(self.domain, value.domain) == []):
            # is LinearOrderedCell with same domain
            return value
        elif value in self.domain:
            return LinearOrderedCell(self.domain, value, value)
        elif isinstance(value, (list, tuple)) and all(map(value in self.domain, value)):
            if len(value) == 1:
                return LinearOrderedCell(self.domain, value[0], value[0])
            elif len(value) == 2:
                return LinearOrderedCell(self.domain, *value)
            else:
                sorted_vals = sorted(value, key=lambda x: self.to_i(x))
                return LinearOrderedCell(self.domain, sorted_vals[0], sorted_vals[-1])
        else:
            raise Exception("Cannot coerce %s into LinearOrderedCell" % (str(value)))

    def to_i(self, val):
        """
        Maps value to position in domain

        :param val: value in the domain
        :returns: int -- index of value in the domain. Returns -1 if val is None

        """
        if val is None:
            return -1
        return self.domain.index(val)

    def is_contradictory(self, other):
        """
        Whether other and self can coexist

        :param other: A LinearOrderedCell or coercible value
        :returns: bool
        :raises: Exception
        
        """
        other = self.coerce(other)
        to_i = self.to_i
        assert to_i(other.low) <= to_i(other.high), "Low must be <= high"
        if max(map(to_i, [other.low, self.low])) <= min(map(to_i, [other.high, self.high])):
            return False
        else:
            return True

    def is_entailed_by(self, other):
        """
        Returns true if Other is more specific than self or if Other is bounded within self.

        :param other: A LinearOrderedCell or coercible value
        :returns: bool
        :raises: Exception
        
        """
        other = self.coerce(other)
        to_i = self.to_i
        return to_i(other.low) >= to_i(self.low) and \
                to_i(other.high) <= to_i(self.high)

    def is_equal(self, other):
        """
        Determines whether two intervals are the same, i.e. every element of each domain is also an element of the other domain, and the low and high of each domain correspond to the low and high of the other

        :param other: A LinearOrderedCell or coercible value
        :returns: bool
        :raises: Exception
        
        """
        other = self.coerce(other)
        return list_diff(self.domain, other.domain) == [] \
                and self.low == other.low \
                and self.high == other.high

    def to_dot(self):
        """
        A string representation of the Cell

        :returns: If the domain consits of a single value, that value is returned. Otherwise, the empty string is returned.

        """
        if self.low == self.high:
            return self.low
        else:
            return ""

    def merge(self, other):
        """
        Merges the two values

        :param other: A LinearOrderedCell or coercible value
        :returns: LinearOrderedCell
        :raises: Contradiction
        
        """
        other = self.coerce(other)
        if list_diff(self.domain, other.domain) != []:
            raise Exception("Incomparable orderings. Different domains")
        if self.is_equal(other):
            # pick among dependencies
            return self
        elif other.is_entailed_by(self):
            return self
        elif self.is_entailed_by(other):
            self.low, self.high = other.low, other.high
        elif self.is_contradictory(other):
            raise Contradiction("Cannot merge %s and %s" % (self, other))
        else:
            # information in both
            to_i = self.to_i
            self.low = self.domain[max(map(to_i, [self.low, other.low]))]
            self.high =self.domain[min(map(to_i, [self.high, other.high]))]
        return self

    def __hash__(self):
        return reduce(lambda x, y: hash(x) ^ hash(y), self.domain + [self.low, self.high], 0)

    def __repr__(self):
        """
        Displays the range
        """
        return "[%s, %s]" % (self.low, self.high)

    __eq__ = is_equal


class ListCell(Cell):
    """
    ListCells contain ordered elements
    """
    def __init__(self, value=None):
        """
        Creates a new ListCell, optionally with an initial value.
        """
        if value:
            if isinstance(value, list):
                self.value = value
            else:
                raise CellConstructionException("ListCells must be given a list")
        else:
            self.value = []

    @staticmethod
    def coerce(value):
        """
        Turns a value into a ListCell

        :param value: The value to be coerced
        :returns: ListCell
        
        """
        if isinstance(value, ListCell):
            return value
        elif isinstance(value, (list)):
            return ListCell(value)
        else:
            return ListCell([value])

    def size(self):
        """
        Returns the number of elements in the list

        :returns: int -- number of elements in the list
        """
        if self.value is None:
            return 0
        else:
            return len(self.value)

    def is_contradictory(self, other):
        """
        Two lists are contradictory if the shorter one is not a prefix of the
        other. (Very strict definition -- could be generalized to subsequence)
        """
        if other.size() > self.size():
            return other.is_contradictory(self)
        # ensure self is bigger or equal size
        if other.size() == 0:
            # empty lists are fine
            return False
        
        # see if any values in the shorter list are contradictory or 
        # unequal
        for i, oval in enumerate(other.value):
            if hasattr(self.value[i], 'is_contradictory') and \
                    self.value[i].is_contradictory(oval):
                # allow comparing cells
                return True
            elif self.value[i] != oval:
                return True
        return False

    def is_entailed_by(self, other):
        """
        Returns True iff the values in this list can be entailed by the other
        list (ie, this list is a prefix of the other)

        :param other: ListCell or coercible value
        :returns: bool
        
        """
        other = ListCell.coerce(other)
        if other.size() < self.size():
            # other is bigger, can't be entailed
            return False
        if self.value is None:
            # list is empty
            return True

        # see if any values in the shorter list are contradictory or 
        # unequal
        for i, oval in enumerate(other.value):
            if i == len(self.value):
                break

            if hasattr(self.value[i], 'is_entailed_by') and \
                   not self.value[i].is_entailed_by(oval):
                # compare cells
                return False 
            elif self.value[i] != oval:
                return False 
        return True 
        
    def is_equal(self, other):
        """
        Whether the lists are equal
        """
        other = ListCell.coerce(other)
        if len(other.value) != len(self.value):
            return False
        
        for i, oval in enumerate(other.value):
            if hasattr(self.value[i], 'is_equal') and \
                   not self.value[i].is_equal(oval):
                # compare cells
                return False 
            elif self.value[i] != oval:
                return False 
        return True 
        
    def merge(self, other):
        """
        Merges two Lists

        :param other: A ListCell or coercible value
        :returns: ListCell
        
        """
        other = ListCell.coerce(other)
        if self.is_equal(other):
            # pick among dependencies
            return self
        elif other.is_entailed_by(self):
            return self
        elif self.is_entailed_by(other):
            self.value = other.value[:]
        elif self.is_contradictory(other):
            raise Contradiction("Cannot merge list '%s' with '%s'" % \
                    (self, other))
        else:
            if len(self.value) > len(other.value):
                self.value = other.value[:]
            # otherwise, return self
        return self

    def append(self, el):
        """
        Idiosynractic method for adding an element to a list
        """
        if self.value is None:
            self.value = [el]
        else:
            self.value.append(el)

    def get_values(self):
        """
        Returns a list containing the elements
        """
        if self.value == None:
            return []
        else:
            return self.value[:]

    def __hash__(self):
        return reduce(lambda x, y: hash(x) ^ hash(y), self.value, 0)

    def __repr__(self):
        if self.value == None:
            return ""
        else:
            return '[' + ', '.join(self.value) + ']'

    __str__ = __repr__
    __eq__ = is_equal


class PrefixCell(ListCell):
    """
    PrefixCells contain lists of paths
    """

    def merge(self, other):
        """
        Merges two prefixes

        :param other: A ListCell or coercible value
        :returns: PrefixCell
        
        """
        other = PrefixCell.coerce(other)
        if self.is_equal(other):
            # pick among dependencies
            return self
        elif other.is_entailed_by(self):
            return self
        elif self.is_entailed_by(other):
            self.value = other.value
        elif self.is_contradictory(other):
            raise Contradiction("Cannot merge prefix '%s' with '%s'" % \
                    (self, other))
        else:
            if len(self.value) > len(other.value):
                self.value = other.value[:]
            # otherwise, return self
        return self

    def __repr__(self):
        if self.value == None:
            return ""
        else:
            return 'p[' + ', '.join(self.value) + ']'

    __str__ = __repr__

