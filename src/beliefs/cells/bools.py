from beliefs.cells import *
from beliefs.cells.exceptions import *

# constants for 3-valued logic
T = True
F = False
U = 'UNKNOWN'


class BoolCell(Cell):
    """
    3-valued logic (T, F, U)
    (U)ndefined means (T v F) ^ -(T ^ F)
    """
    def __init__(self, value=None):
        """ Initializes a new BoolCell, default to 'U' """
        if not value in [T, F]:
            self.value = U
        else:
            self.value = value
        assert self.value in [T, F, U], \
                "Invalid Bool value %d " % (self.value,)

    @staticmethod
    def coerce(value):
        """
        Coerces a Bool, None, or int into Bit/Propositional form. If *value* is an int, must be -1, 0, or 1.

        .. note::
            T, F, and U can be used in place of ``True``, ``False``, and ``'UNKNOWN'``, respectively.
        
        :param value: The value to coerce
        :type value: bool, int
        :returns:  BoolCell
        :raises: CellConstructionFailure, CoercionFailure

        >>> f1 = BoolCell.coerce(0)
        >>> f1
        False
        >>> f2 = BoolCell.coerce(F)
        >>> f2
        False
        >>> t1 = BoolCell.coerce(1)
        >>> t1
        True
        >>> t2 = BoolCell.coerce(T)
        >>> t2
        True
        
        """
        if isinstance(value, BoolCell):
            return value
        elif isinstance(value, Cell):
            raise CellConstructionFailure("Cannot convert %s to BoolCell" % \
                    type(value))
        elif value in [1, T]:
            return BoolCell(T)
        elif value in [0, -1, F]:
            return BoolCell(F)
        elif value in [None, U]:
            return BoolCell(U)
        else:
            raise CoercionFailure("Don't know how to coerce %d to Bool" % \
                    (value))

    def is_entailed_by(self, other):
        """
        Returns True if the other is as or more specific than self

        :param other: The BoolCell or coercible value that may entail self
        :type other: BoolCell, bool, int
        :returns:  bool
        :raises: CellConstructionFailure, CoercionFailure

        >>> x = BoolCell(T)
        >>> y = BoolCell(F)
        >>> z = BoolCell(U)
        >>> x.is_entailed_by(U)
        False
        >>> y.is_entailed_by(F)
        True
        >>> y.is_entailed_by(U)
        False
        >>> z.is_entailed_by(x)
        True

        """
        other = BoolCell.coerce(other)
        if self.value == U or other.value == self.value:
            return True
        return False

    def entails(self, other):
        """
        Inverse of ``is_entailed_by``. Returns True if self is as or more specific than other.

        :param other: The BoolCell or coercible value to check if it is entailed by self
        :type other: BoolCell, bool, int
        :returns:  bool
        :raises: CellConstructionFailure, CoercionFailure

        >>> x = BoolCell(T)
        >>> y = BoolCell(F)
        >>> z = BoolCell(U)
        >>> x.entails(T)
        True
        >>> x.entails(U)
        True
        >>> y.entails(T)
        False
        >>> y.entails(F)
        True
        >>> z.entails(U)
        True
        >>> z.entails(F)
        False

        """
        other = BoolCell.coerce(other)
        return other.is_entailed_by(self)
        
    def is_contradictory(self, other):
        """
        Determines if two cells are contradictory. Returns a boolean.

        :param other: The BoolCell or value that may contradict self.
        :type other: BoolCell, bool, int
        :returns:  bool
        :raises: CellConstructionFailure, CoercionFailure

        >>> x = BoolCell(T)
        >>> y = BoolCell(F)
        >>> z = BoolCell(U)
        >>> x.is_contradictory(y)
        True
        >>> y.is_contradictory(x)
        True
        >>> z.is_contradictory(x)
        False
        >>> z.is_contradictory(y)
        False
        >>> z.is_contradictory(U)
        False

        """
        other = BoolCell.coerce(other)
        if self.value == U or other.value == U or (self.value == other.value):
            return False
        else:
            return True

    def to_json(self):
        """ Returns JSON representation of BoolCell"""
        return self.value

    def from_json(self, other):
        """ Initializes from JSON representation """
        self.value = other

    def is_equal(self, other):
        """
        Tests whether two Cells are equal. Returns a boolean.

        :param other: BoolCell or coercible value to be tested
        :type other: BoolCell, bool, int
        :returns: bool
        :raises: CoercionFailure

        >>> x = BoolCell(T)
        >>> y = BoolCell(F)
        >>> x.is_equal(x)
        True
        >>> x.is_equal(T)
        True
        >>> y.is_equal(x)
        False
        
        """
        try:
            other = BoolCell.coerce(other)
            return self.value == other.value
        except CellConstructionFailure:
            return False

    def merge(self, other):
        """
        Merges two BoolCells. A Contradiction is raised if the two BoolCells are contradictory.

        :param other: BoolCell or coerce-able value to be merged
        :type other: BoolCell, bool, int
        :returns: BoolCell
        :raises: CellConstructionFailure, CoercionFailure, Contradiction

        >>> v = BoolCell(U)
        >>> w = BoolCell(U)
        >>> z = BoolCell(U)
        >>> v.merge(T)
        True
        >>> z.merge(F)
        False
        >>> w.merge(U)
        'UNKNOWN'
        """
        other = BoolCell.coerce(other)
        if self.is_equal(other):
            # pick among dependencies
            return self
        elif other.is_entailed_by(self):
            return self
        elif self.is_entailed_by(other):
            self.value = other.value
        elif self.is_contradictory(other):
            raise Contradiction("Cannot merge T and F")
        else:
            raise Exception
        return self

    def __sub__(self, other):
        """
        Returns a difference structure
        """
        if self.is_equal(other):
            return None
        if self.is_entailed_by(other):
            # other has more info
            return [other.value]
        else:
            raise NotDifferentiable

    def __repr__(self):
        return "%r" % (self.value,)

    def __hash__(self):
        """
        Returns a hash that is different for T, F and U
        """
        return hash(self.value)

    __eq__ = is_equal

def test_bool_cell_hash_functions():
    b1 = BoolCell()
    b2 = BoolCell(U)
    b3 = BoolCell(F)
    b4 = BoolCell(T)
    assert hash(b1) == hash(b2)
    assert hash(b2) != hash(b3)
    assert hash(b3) != hash(b4)
    assert hash(b2) != hash(b4)
    assert b1 == b2
    assert b2 != b4
    assert b2 != b3
    assert b3 != b4

if __name__ == '__main__':
    test_bool_cell_hash_functions()
    bu = BoolCell()
    print bu
    bt = BoolCell(T)
    bf = BoolCell(F)

