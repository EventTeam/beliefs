from beliefs.cells import *
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
        Coerces a Bool, None, or int into Bit/Propositional form
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
        """ If the other is as or more specific than self"""
        other = BoolCell.coerce(other)
        if self.value == U or other.value == self.value:
            return True
        return False

    def entails(self, other):
        """ Inverse is_entailed_by """
        other = BoolCell.coerce(other)
        return other.is_entailed_by(self)
        
    def is_contradictory(self, other):
        """ Determines if two cells are contradictory. Returns a boolean."""
        other = BoolCell.coerce(other)
        if self.value == U or other.value == U or (self.value == other.value):
            return False
        else:
            return True

    def to_dot(self):
        """ Returns value as a string"""
        return "%s" % (self.value)

    def to_json(self):
        """ Returns JSON representation of BoolCell"""
        return self.value

    def from_json(self, other):
        """ Initializes from JSON representation """
        self.value = other

    def is_equal(self, other):
        """ Tests whether two Cells are equal. Returns a boolean. """
        try:
            other = BoolCell.coerce(other)
            return self.value == other.value
        except CellConstructionFailure:
            return False

    def merge(self, other):
        """
        Merges two BoolCells
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

