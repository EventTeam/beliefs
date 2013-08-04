from cell import *
import numpy as np

class IntervalCell(Cell):
    """
    Implements an interval cell along with interval algebra
    """

    def __init__(self, low=None, high=None):
        """
        Creates a new IntervalCell with values restricted to between *low* and *high*.

        :param low,high: The boundaries of the interval
        :type low,high: float,int
        :raises: CellConstructionFailure
        
        """
        self.low = -np.inf
        self.high = np.inf
        
        if low is not None:
            self.low = low
        if high is not None:
            self.high = high

        if self.high < self.low:
            raise CellConstructionFailure

    @staticmethod
    def coerce(value):
        """
        Takes in either a single number (float, int), a list, or a tuple and returns the
        [low, high] in the standard interval form. In the case of a single *value*, the low and high will both be the single value. In the case of a list or tuple, the low and high will be the min and max of the collection, respectively.

        :param value: The the number or collection of numbers to be used for the low and high boundaries
        :type value: int, float, complex, list, tuple
        :returns: IntervalCell
        :raises: Exception

        >>> a = IntervalCell.coerce(5)
        >>> a
        5.00
        >>> b = IntervalCell.coerce([3,7])
        >>> b
        [3.00,7.00]
        >>> c = IntervalCell.coerce((1,6,5,9,2))
        >>> c
        [1.00,9.00]
        
        """
        is_number = lambda x: isinstance(x, (int, float, complex)) #is x an instance of those things
        if isinstance(value, IntervalCell) or issubclass(value.__class__,IntervalCell): 
            #if intervalcell or subclass, return the subclass
            return value
        elif is_number(value):
            return IntervalCell(value, value)
        elif hasattr(value, 'low') and hasattr(value, 'high'):
            # duck type
            assert value.low <= value.high, "Invalid low/high in %s" % str(value)
            return value
        elif isinstance(value, (list, tuple)) and all(map(is_number, value)):
            if len(value) == 1:
                low, high = value[0], value[0]
            elif len(value) == 2:
                low, high = value
            else:
                low, high = min(value), max(value)
            if high < low:
                raise Contradiction("Low must be lte High") 
            return IntervalCell(low, high)
        else:
            raise Exception("Don't know how to coerce %s" % (type(value)))

    def stem(self):
        """
        Creates a new instance with bounds of 0 to infinity

        :returns: IntervalCell

        >>> x = IntervalCell(1,1)
        >>> y = x.stem()
        >>> y
        [0.00,inf]
        """
        return self.__class__(0, np.inf)

    def size(self):
        """
        Number of possible values in the interval.  Boundaries are inclusive

        :returns: int -- Length of interval

        >>> a = IntervalCell(1,2)
        >>> b = IntervalCell(12,19)
        >>> a.size()
        2
        >>> b.size()
        8
        """
        return (self.high - self.low) + 1 

    def is_contradictory(self, other):
        """
        Determines whether other and self can coexist. Two intervals are contradictory if they are disjoint, i.e. if their intersection is empty

        :param other: IntervalCell or coercible value
        :returns: bool
        :raises: Exception

        >>> w = IntervalCell(1,2)
        >>> x = IntervalCell(1,1)
        >>> y = IntervalCell(2,2)
        >>> z = IntervalCell(0,3)
        >>> x.is_contradictory(y)
        True
        >>> w.is_contradictory(z)
        False
        >>> x.is_contradictory(w)
        False
        """
        other = IntervalCell.coerce(other)
        assert other.low <= other.high, "Low must be <= high"
        if max(other.low, self.low) <= min(other.high, self.high):
            return False
        else:
            return True

    def is_entailed_by(self, other):
        """
        Returns true if other is more specific than self, i.e. other is bounded within self.

        :param other: IntervalCell or coercible value
        :returns: bool
        :raises: Exception

        >>> x = IntervalCell(1,1)
        >>> y = IntervalCell(2,2)
        >>> z = IntervalCell(0,3)
        >>> z.is_entailed_by(x)
        True
        >>> z.is_entailed_by(y)
        True
        >>> x.is_entailed_by(y)
        False
        """
        other = IntervalCell.coerce(other)
        return other.low >= self.low and other.high <= self.high

    def is_equal(self, other):
        """
        Returns true if two intervals are the same

        :param other: IntervalCell or coercible value
        :returns: bool
        :raises: Exception

        >>> x = IntervalCell(1,1)
        >>> z = IntervalCell(0,3)
        >>> x.is_equal(1)
        True
        >>> z.is_equal([0,3])
        True
        >>> x.is_equal(z)
        False
        
        """
        other = IntervalCell.coerce(other)
        return other.low == self.low and other.high == self.high

    def merge(self, other):
        """
        Merges the two values. The *self* argument is modified, while *other* is not.

        :param other: IntervalCell or coercible value
        :returns: bool
        :raises: Exception

        >>> x = IntervalCell(0,3)
        >>> y = IntervalCell(2,2)
        >>> a = x.merge(y)
        >>> a
        2.00
        
        .. note::
            ``merge`` modifies the *self* argument as a side effect. 

            >>> w = IntervalCell(1,7)
            >>> z = IntervalCell(3,9)
            >>> b = w.merge(z)
            >>> b
            [3.00,7.00]
        
            w has been modified.
        
            >>> w
            [3.00,7.00]
        
            z has not.
        
            >>> z
            [3.00,9.00]
        
        """
        other = IntervalCell.coerce(other)
        if self.is_equal(other):
            # pick among dependencies
            return self
        elif other.is_entailed_by(self):
            return self
        elif self.is_entailed_by(other):
            self.low, self.high = other.low, other.high
        elif self.is_contradictory(other):
            #import traceback
            #for line in traceback.format_stack(): print line.strip()

            raise Contradiction("Cannot merge [%0.2f, %0.2f] with [%0.2f, %0.2f]" \
                    % (self.low, self.high, other.low, other.high))
        else:
            # information in both
            self.low = max(self.low, other.low)
            self.high = min(self.high, other.high)
        return self

    def __cmp__(self, other):
        """
        Uses 'self.low' to make the comparison

        Returns -1 if self < other
                0 if self == other
                1 if other > self
        """
        other = IntervalCell.coerce(other)
        if other.low == self.low and other.high == self.high:
            return 0
        elif self.low < other.low:
            return -1
        else:
            return 1

    def __repr__(self):
        """
        Displays the interval
        """
        if self.low == self.high:
            return "%0.2f" % (self.low,)
        else:
            return "[%0.2f, %0.2f]" % (self.low, self.high)

    def __add__(self, other):
        """
        Interval addition
        """
        other = IntervalCell.coerce(other)
        return IntervalCell(self.low + other.low, self.high + other.high)

    def __sub__(self, other):
        """
        Subtraction
        """
        return IntervalCell(self.low - other.high, self.high - other.low)

    def __mul__(self, other):
        """
        Interval Multiplication
        """
        other = IntervalCell.coerce(other)
        combos = [self.low * other.low,
                  self.low * other.high,
                  self.high * other.low,
                  self.high * other.high]
        return IntervalCell(min(combos), max(combos))

    def __le__(self, new_upper):
        """ Overload =<  
        
        Note:  we're overloading <= and >=, not < and >, because IntervalCell considers
        its boundaries as inclusive.   Removing the inequality requires setting the inclusive
        boundary to 'one less' than the current boundary
        """
        if isinstance(new_upper, IntervalCell):
            new_upper = new_upper.low
        return self.merge(IntervalCell(self.low, new_upper))
    
    def __ge__(self, new_lower):
        """ Overload >=  """
        if isinstance(new_lower, IntervalCell):
            new_lower = new_lower.high
        return self.merge(IntervalCell(new_lower, self.high))

    def __int__(self):
        """ Integer type conversion """
        assert self.low == self.high, "Cannot be converted to int"
        return int(self.low)

    def __float__(self):
        """ Float type conversion """
        assert self.low == self.high, "Cannot be converted to float"
        return float(self.low)

    def __div__(self, other):
        """
        Division (checks for 0s)
        """
        other = IntervalCell.coerce(other)
        if other.high == 0:
            if other.low == 0:
                raise ZeroDivisionError("Cannot divide by interval [0,0]")
            return  IntervalCell(-np.inf, 1.0 / other.low)
        elif other.low == 0:
            return IntervalCell(1.0 / other.high, np.inf)
        return self * IntervalCell(1.0 / other.low, 1.0 / other.high)

    def map(self, other, function):
        """
        Applies a mathematic function to the interval arithmetic template:
        generate all combinations of low/high values and then take the widest
        bounds (min/max) for the result.

        :param other: IntervalCell or coercible value
        :type other: IntervalCell
        :param function: Mathematical function to be applied to the bounds of the interval. Must take two arguments and return a number
        :type function: function
        :returns: IntervalCell
        :raises: Exception

        >>> a = IntervalCell(1,4)
        >>> b = IntervalCell(3,5)
        >>> result = a.map(b,lambda x,y: x+y)
        >>> result
        [4.00,9.00]
        >>> result = a.map(b,lambda x,y: x-y)
        >>> result
        [-4.00,1.00]
        """
        other = IntervalCell.coerce(other)
        # check the arity of the function
        import inspect
        arity = len(inspect.getargspec(function).args)

        if arity == 2:
            combos = [function(self.low, other.low),
                      function(self.low, other.high),
                      function(self.high, other.low),
                      function(self.high, other.high)]
            return IntervalCell(min(combos), max(combos))
        else:
            raise Exception("Cannot apply function of arity %i " % (arity))

    def __contains__(self, other):
        """ Allows the use of Python's 'in' syntax """
        return self.low <= other <= self.high

    def __hash__(self):
        """ Unique hash for interval """
        hval = 0
        hval = hash(self.low) * 2  + hash(self.high) * 3 + hash(self.high-self.low) * 5 
        return hval

    def get_tuple(self):
        """
        Returns (low, high) tuple

        >>> x = IntervalCell(1,2)
        >>> xTuple = x.get_tuple()
        >>> xTuple
        (1,2)

        """
        return (self.low, self.high)

    '''def to_dot(self):
        """
        Returns a scalar or None
        """
        if self.low == self.high:
            return self.low
        else:
            return None'''

    def to_latex(self):
        """ Returns an interval representation """
        if self.low == self.high:
            if self.low * 10 % 10 == 0:
                return "{0:d}".format(int(self.low))
            else:
                return "{0:0.2f}".format(self.low)
        else:
            t = ""
            if self.low == -np.inf:
                t += r"(-\infty, "
            elif self.low * 10 % 10 == 0:
                t += r"[{0:d}, ".format(int(self.low))
            else:
                t += r"[{0:0.2f}, ".format(self.low)
            if self.high == np.inf:
                t += r"\infty)"
            elif self.high * 10 % 10 == 0:
                t += r"{0:d}]".format(int(self.high))
            else:
                t += r"{0:0.2f}]".format(self.high)
            return t

    def __abs__(self):
        """ Absolute value """
        if self.low == self.high:
            return abs(self.low)
        else:
            return IntervalCell(min(abs(self.low), abs(self.high)), max(abs(self.low), abs(self.high)))

    __eq__ = is_equal
    __len__ = size

<<<<<<< HEAD
=======

if __name__ == '__main__':

    def test_absolute_values():
        # for intervals
        x = IntervalCell(1,20)
        y = IntervalCell(19,100)
        assert abs(x-y) == abs(y-x)
>>>>>>> 68f8e1246b8e0b73a1c58ee71590b3fa87d3b5bb

def test_absolute_values():
    # for intervals
    x = IntervalCell(1,20)
    y = IntervalCell(19,100)
    assert abs(x-y) == abs(y-x)

    # for single numbers
    x = IntervalCell(19,19)
    y = IntervalCell(20,20)
    assert abs(x-y) == abs(y-x)


def test_hashes():
    """ Tests for cases where LOW and HIGH values of the interval
    have the same sum, the same diff, etc. """

    def alldiff(iterable, f=lambda x: x):
        mapped = map(f, iterable)
        return len(mapped) == len(set(mapped))


    test_cases = []
    test_cases += [IntervalCell(2,2)]
    test_cases += [IntervalCell()]
    test_cases += [IntervalCell(1,3)]
    test_cases += [IntervalCell(0,4)]
    test_cases += [IntervalCell(0,2)]
    test_cases += [IntervalCell(2,5)]
    test_cases += [IntervalCell(-3,-1)]
    assert alldiff(test_cases, hash)

    # float / int equivalence
    assert hash(IntervalCell(0,2)) == hash(IntervalCell(0.0,2.0))

if __name__ == '__main__':
    x = IntervalCell(3, 38.2)
    print x.to_latex()
    x = IntervalCell(0, 38)
    print x.to_latex()

