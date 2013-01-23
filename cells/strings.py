from .cell import *
import re

class StringCell(Cell):
    """
    Strings can be merged when one is a subsequence of another
    """
    def __init__(self, value=None):
        """
        Creates a new StringCell, optionally with an initial value.
        """
        if value:
            value = value.lower().strip()
        self.value = value

    @staticmethod
    def coerce(value):
        """
        Turns value into a string
        """
        if isinstance(value, StringCell):
            return value
        elif isinstance(value, (str, unicode)):
            return StringCell(value)
        else:
            raise CoercionFailure("Cannot coerce %s to StringCell" % (value))

    def is_contradictory(self, other):
        """
        Can these two strings coexist ?
        """
        other = StringCell.coerce(other)

        if self.value is None or other.value is None:
            # None = empty, and won't contradict anything
            return False

        def sequence_in(s1, s2):
            """Does `s1` appear in sequence in `s2`?"""
            return bool(re.search(".*".join(s1), s2))

        return not sequence_in(self.value, other.value) and \
            not sequence_in(other.value, self.value)

    def is_entailed_by(self, other):
        """
        Returns True iff self's sequence is None or contained within Other's
        """
        other = StringCell.coerce(other)
        if self.value is None or self.value == "":
            return True
        if other.value is None:
            return False

        def sequence_in(s1, s2):
            """Does `s1` appear in sequence in `s2`?"""
            return bool(re.search(".*".join(s1), s2))
        return sequence_in(self.value, other.value)

    def is_equal(self, other):
        """
        Whether two strings are equal
        """
        other = StringCell.coerce(other)
        empties = [None,'']
        if self.value in empties and other.value in empties:
            return True
        return self.value == other.value

    def merge(self, other):
        """
        Merges two strings
        """
        other = StringCell.coerce(other)
        if self.is_equal(other):
            # pick among dependencies
            return self
        elif other.is_entailed_by(self):
            return self
        elif self.is_entailed_by(other):
            self.value = other.value
        elif self.is_contradictory(other):
            raise Contradiction("Cannot merge string '%s' with '%s'" % \
                    (self, other))
        else:
            self._perform_merge(other)
        return self

    def _perform_merge(self, other):
        """
        Merges the longer string
        """
        if len(other.value) > len(self.value):
            self.value = other.value[:]
        return True

    def to_dot(self):
        """
        Representation for Graphviz's dot
        """
        return self.value

    def get_value(self):
        """
        Returns value if it exists or an empty string
        """
        if self.value:
            return self.value
        else:
            return ''

    def __repr__(self):
        if self.value == None:
            return ""
        else:
            return self.value

    __str__ = __repr__
    __eq__ = is_equal


class NameCell(StringCell):
    pass
