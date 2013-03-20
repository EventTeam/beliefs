from cell import *
import operator
import datetime
import time
import itertools

SIMPLE_TYPES = (int, long, float, bool, dict, basestring, list)

class DictCell(Cell):
    """
    This is a wrapper for a dictionary of cells.  Can be compared with another
    DictCell.

    Unlike the other primitive structures, a DictCell cannot be coerced into something
    else.

    :param from_dict: Optional parameter specifying initial dictionary, where the value of each (key,value) pair must be a Cell. Defaults to an empty dictionary.
    :type from_dict: dict
    """
    HASATTR = 0

    def __init__(self, from_dict=None):
        """
        Takes a dictionary object that contains the names (keys) and
        their corresponding cells (values)
        """
        # check key names for conflicts with the classes own attributes
        # and verify that all values are subclasses of Cell
        if from_dict is None:
            from_dict = {}

        for key, val in from_dict.items():
            if not isinstance(val, Cell):
                if isinstance(val, dict):
                    from_dict[key] = DictCell(val)
                else:
                    raise CellConstructionFailure("Value of property '%s' must be " % (key,) +
                            "an instance of Cell, not %s" % (type(val)))
        self.__dict__['p'] = from_dict

    def __setattr__(self, k, v):
        """ Merges or creates a new value for a property in the dictionary """
        if k in self.__dict__['p']:
            return self[k].merge(v)
        else:
            self.__dict__['p'][k] = v
            return self[k]

    def __getitem__(self, k):
        """ Standard dictionary member access syntax.  Given a DictCell, `d`, to 
        access property `size`, you would call: `d['size']` """
        if not hasattr(self, 'p'):
            raise AttributeError("No property attribute 'p'")
        if k in self.__dict__['p']:
            return self.p[k]
        elif hasattr(self, k):
            return self.__dict__[k]
        else:
            raise AttributeError("No attribute '%s'" % (k,))

    def __setitem__(self, k, val):
        """ Standard dictionary member update syntax Given a DictCell, `d`, to 
        set property `size` to value 3, you would call: `d['size']` = 3 """
        if not hasattr(self, 'p'):
            raise AttributeError("No property attribute 'p'")
        if k in self.__dict__['p']:
            return self.p[k].merge(val)
        else:
            return object.__setattr__(self, k, val)

    def __delitem__(self, k):
        """ Deletes an attribute k """
        if not hasattr(self, 'p'):
            raise AttributeError("No property attribute 'p'")
        if k in self.__dict__['p']:
            del self.__dict__['p'][k]

    def contains(self, key_or_keypath):
        """ Allows the 'in' operator to work for checking if a particular key (or keypath)
        is inside the dictionary. 

        :param key_or_keypath: A single key or a path of keys in the form of a list
        :returns: bool"""
        if isinstance(key_or_keypath, list):
            if len(key_or_keypath) == 0:
                # empty list is root
                return False
            val = self 
            next_key = None
            for next_key in key_or_keypath:
                if next_key in val:
                    val = val[next_key]
                else:
                    return False
            return True
        else:
            return key_or_keypath in self.__dict__['p']
            
    def get_value_from_path(self, keypath):
        """
        Returns the value at the end of keypath (or None)
        keypath is a list of keys, e.g., ["key", "subkey", "subsubkey"]

        :param keypath: A list of keys representing a path through nested dictionaries
        :type keypath: list
        :returns: value associated with final key in *keypath*
        """
        if isinstance(keypath, list):
            if len(keypath) == 0:
                # empty list is root
                return 
            val = self 
            for next_key in keypath:
                val = val[next_key]
            return val
        else:
            return self.__dict__['p'][keypath]

    def is_entailed_by(self, other):
        """
        Whether all of self's keys (and values) are in (and within) other's

        :param other: A DictCell to check
        :type other: DictCell
        :returns: bool
        """
        for (s_key, s_val) in self:
            if s_key in other:
                if not other[s_key].entails(s_val):
                    return False
            else:
                return False
        return True


    def entails(self, other):
        """ Whether the target of the other belief state is strictly more
        general than the caller belief state

        :param other: A DictCell to check
        :type other: DictCell
        :returns: bool

        """
        return other.is_entailed_by(self)

    def is_contradictory(self, other):
        """
        Returns True if the two DictCells are unmergeable, i.e. if the two DictCells share a key, but the Cells associated with those keys are unMergeable.

        :param other: DictCell to check
        :type other: DictCell
        :returns: bool
        :raises: Exception
        """
        if not isinstance(other, DictCell):
            raise Exception("Incomparable")
        for key, val in self:
            if key in other.__dict__['p'] \
                    and val.is_contradictory(other.__dict__['p'][key]):
                return True
        return False

    def is_equal(self, other):
        """ Two DictCells are equal when they share ALL Keys,  and all of their 
        ``is_equal()`` methods return True.  This ensures substructure equality.

        :parameter other: DictCell to compare
        :type other: DictCell
        :returns: bool
        """
        if not isinstance(other, DictCell):
            return False
        for (this, that) in itertools.izip_longest(self, other):
            if this[0] != that[0]:
                # compare key names
                return False
            if not this[1].is_equal(that[1]):
                # compare cells
                return False
        return True
        

    def __iter__(self):
        """ Iterate through first-level of sorted keys and values """
        return iter(sorted(self.__dict__['p'].items(), key=operator.itemgetter(0)))

    def __hash__(self):
        """ Iterate through all members and hash 'em """
        hash_val = 0
        for key, val in self:
            hash_val +=  hash(key) + hash(val)
        if hash_val == -2:
            hash_val = -1
        return hash_val
        
    def merge(self, other):
        """
        Merges two complex structures (by recursively merging their parts).
        Missing-parts do not trigger contradictions.

        :param other: DictCell to merge
        :type other: DictCell
        :returns: DictCell
        :raises: Exception, Contradiction
        
        """
        if not isinstance(other, DictCell):
            raise Exception("Incomparable")
        if self.is_equal(other):
            # pick among dependencies
            return self
        elif other.is_entailed_by(self):
            return self
        elif self.is_entailed_by(other):
            self.__dict__['p'] = other.__dict__['p'].copy()
        elif not self.is_contradictory(other):
            # partial information in both, add from other
            for o_key, o_val in other:
                if not o_key in self.__dict__['p']:
                    self.__dict__['p'][o_key] = o_val
                else:
                    self.__dict__['p'][o_key].merge(o_val)
        else:
            raise Contradiction("Dictionaries are contractory, cannot Merge")
        return self

    def __repr__(self, indent=0):
        """ Pretty prints a string representing the structure of the tree.  """
        result = ""
        for i, (key, val) in enumerate(self):
            if i != 0:  result += " " * indent
            if isinstance(val, DictCell):
                result += "%s : " % (key)
                result += val.__repr__(indent+len(key)+3)
            else:
                result += "%s : %s " % (key, val)
            result += "\n"
        return result 

    def to_dict(self):
        """
        This method converts the DictCell into a python `dict`.  This is useful
        for JSON serialization.

        :returns: dict
        """
        output = {}
        for key, value in self.__dict__['p'].iteritems():
            if value is None or isinstance(value, SIMPLE_TYPES):
                output[key] = value
            elif hasattr(value, 'to_dot'):
                output[key] = value.to_dot()
            elif hasattr(value, 'to_dict'):
                output[key] = value.to_dict()
            elif isinstance(value, datetime.date):
                # Convert date/datetime to ms-since-epoch ("new Date()").
                ms = time.mktime(value.utctimetuple()) * 1000
                ms += getattr(value, 'microseconds', 0) / 1000
                output[key] = int(ms)
            elif isinstance(value, dict):
                output[key] = []
            else:
                raise ValueError('cannot encode ' + repr(key))

        return output

    def keys(self):
        """
        Returns a list of the top-level keys in the DictCell

        :returns: list
        """
        return [k for k, _ in self]
        
    def values(self):
        """
        Returns a list of the top-level values in the DictCell

        :returns: list
        """
        return [v for _, v in self]

    def items(self):
        """
        Returns both keys and values in dictionary

        :returns: list of tuples
        """
        return [(k,v) for k, v in self]

    __eq__ = is_equal
    __contains__ = contains


