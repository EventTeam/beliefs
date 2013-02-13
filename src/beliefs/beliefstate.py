from copy import copy
from collections import OrderedDict, defaultdict
from beliefs.cells import *
from belief_utils import choose
import itertools

class BeliefState(DictCell):
    """
    Represents a beliefstate, a partial information object *about* specific targets.
    A beliefstate is a continuum between individual cells and entire classes of cells.
        
    Suppose the domain has entities/cells: 1,2,3.  A valid beliefstate represents the possible groupings 
    of these entities; a single grouping is called a *referent*.  A beliefstate can be about
    "all referents of size two", for example, and computing the beliefstate's contextset would 
    yeild the targets {1,2}, {2,3}, and {1,3}.
    
    In addition to containing a description of the intended targets, a belief state contains information
    about the relational constraints (such as arity size), and linguistic decisions.
    """
    def __init__(self, contextset=None):
        """ 
        Initializes an empty belief state, and stores the contextset (if specified) 
        into self.contextset. 
         
        By default, belief states are given the 'S' part of speech and an empty
        environment variable stack.

        The other, more common, way to create a belief state is to call bs.copy() on 
        a previous belief state.
        """
        self.__dict__['pos'] = 'S'  # syntactic state
        self.__dict__['contextset'] = contextset
        self.__dict__['environment_variable'] = {}

        default_structure = {'target': DictCell(),
                'speaker_goals': {'targetset_arity': IntervalCell(0, 10000),
                                  'is_in_commonground': BoolCell()}}

        DictCell.__init__(self, default_structure)
    
    def set_pos(self, pos):
        """
        Sets the BeliefState's part of speech 
        """
        self.__dict__['pos'] = pos

    def get_pos(self):
        """ Returns Part of Speech"""
        return self.__dict__['pos']

    def set_environment_variable(self, key, val):
        """ Sets a variable if that variable is not already set """
        if self.get_environment_variable(key) in [None, val]:
            self.__dict__['environment_variable'][key] = val
        else:
            raise Contradiction

    def get_environment_variable(self, key, default=None, pop=False):
        if key in self.__dict__['environment_variable']:
            val = self.__dict__['environment_variable'][key]
            if pop:
                del self.__dict__['environment_variable'][key]
            return val
        else:
            return default

    def has_contextset(self):
        """
        Returns True if the BeliefState has a context set defined -- meaning a set
        of external referents.
        """
        return self.__dict__['contextset'] is not None

    def iter_breadth_first(self, root=None):
        """ Traverses the belief state's structure breadth-first """
        if root == None:
            root = self
        yield root
        last = root 
        for node in self.iter_breadth_first(root):
            if isinstance(node, DictCell):
                # recurse
                for subpart in node:
                    yield subpart
                    last = subpart
            if last == node:
                return

    def find_path(self, test_function=None, on_targets=False):
        """
        General helper method that iterates breadth-first over the contextset's
        cells and returns a path where the test_function is True
        """
        assert self.has_contextset(), "need context set"

        if not test_function:
            test_function = lambda x, y: True
           
        def find_path_inner(part, prefix):
            name, structure = part
            if test_function(name, structure):
                yield prefix + [name]
            if isinstance(structure, DictCell):
                for sub_structure in structure:
                    for prefix2 in find_path_inner(sub_structure,\
                            prefix[:] + [name]):
                        yield prefix2

        prefix = []
        if on_targets:
            # apply search to the first target
            results = []
            for _, instance in self.iter_singleton_referents():
                for part in instance:
                    for entry in find_path_inner(part, prefix[:]):
                        results.append(['target'] + entry)
                while results:
                    yield results.pop()
                break # only use first instance
        else:
            # apply search to self
            for part in self:
                for entry in find_path_inner(part, prefix[:]):
                    yield entry


    def get_ordered_values(self, keypath, reverse=False):
        """
        Retrieves the contextset's values for the specified keypath.
        """
        values = defaultdict(int)  # value -> ct 
        if keypath[0] == 'target':
            # instances start with 'target' prefix, but 
            # don't contain it, so we remove it here.
            keypath = keypath[1:]
        for _, instance in self.iter_singleton_referents():
            values[instance.get_value_from_path(keypath)] += 1
        # sort the values
        values_sorted = OrderedDict()
        for key in sorted(values.keys(), reverse=reverse):
            values_sorted[key] = values[key]
        return values_sorted

    def get_paths_for_attribute_set(self, keys):
        """
        Given a list/set of keys (or one key), returns the parts that have
        all of the keys in the list.

        DOES NOT WORK WITH TOP LEVEL OBJECTS (since these are not indexed by
        the path)

        These paths are not pointers to the objects themselves, but tuples of
        prefixes that allow us to (attempt) to look up that object in any
        belief state.
        """
        if not isinstance(keys, (list, set)):
            keys = [keys]

        has_all_keys = lambda name, structure: \
                all(map(lambda k: k in structure, keys))
        return self.find_path(has_all_keys, on_targets=True)

    def get_parts(self):
        """
        Searches for all DictCells (with nested structure)
        """
        return self.find_path(lambda x: isinstance(x[1], DictCell), on_targets=True)

    def get_paths_for_attribute(self, attribute_name):
        """
        Returns items with a particular name
        """
        has_name = lambda name, structure:  name == attribute_name
        return self.find_path(has_name, on_targets=True)

    def merge(self, keypath, value, op='set'):
        """
        First gets the cell at BeliefState's keypath, or creates a new cell 
        from the first target that has that keypath (This could mess up if the
        member its copying from has a different Cell or domain for that keypath.)
        Second, this merges that cell with the value
        """
        if keypath not in self:
            first_instance = None
            if keypath[0] == 'target':
                has_targets = False 
                for _, referent in self.iter_singleton_referents():
                    has_targets = True
                    if keypath[1:] in referent:
                        first_referent = referent
                        break
                if first_referent is None:
                    # this happens when none of the available targets have the
                    # path that is attempted to being merged to
                    if has_targets:
                        raise CellConstructionFailure("Cannot merge; no targe: %s" \
                            % (str(keypath)))
                    else:
                        # this will always happen when size is 0
                        raise CellConstructionFailure("Empty belief state")
                # find the type and add it to the 
                cell = first_referent.get_value_from_path(keypath[1:]).stem()
                self.add_cell(keypath, cell)
            else:
                # should we allow merging undefined components outside of target?
                raise NotImplemented

        cell = self
        if not isinstance(keypath, list):
            keypath = [keypath]
        for key in keypath:
            cell = cell[key]
        # perform operation (set, <=, >= etc)
        return getattr(cell, op)(value)
   
    def add_cell(self, keypath, cell):
        """ Adds a new cell to the end of `keypath` of type `cell`"""
        keypath = keypath[:] # copy
        inner = self  # the most inner dict where cell is added
        cellname = keypath  # the name of the cell
        assert keypath not in self, "Already exists: %s " % (str(keypath))
        if isinstance(keypath, list):
            while len(keypath) > 1:
                cellname = keypath.pop(0)
                if cellname not in inner:
                    inner.__dict__['p'][cellname] = DictCell()
                inner = inner[cellname] # move in one
            cellname = keypath[0]
        # now we can add 'cellname'->(Cell) to inner (DictCell)
        inner.__dict__['p'][cellname] = cell
        return inner[cellname]

    def entails(self, other):
        """
        One beliefstate entails another beliefstate iff the other state's cells are all equal or 
        more general than the caller's parts.  That means the other state must have at least 
        all of the same keys/components.  """
        return other.is_entailed_by(self)

    def is_entailed_by(self, other):
        """
        Given two beliefstates, returns True iff the calling instance
        implies the other beliefstate, meaning it contains at least the same
        structure (for all structures) and all values (for all defined values).
        
        Inverse of `entails`.
        """
        for (s_key, s_val) in self:
            if s_key in other:
                if not hasattr(other[s_key], 'implies'):
                    raise Exception("Cell for %s is missing implies()" % s_key)
                if not other[s_key].implies(s_val):
                    return False
            else:
                return False
        return True

    def is_equal(self, other):
        """
        Two beliefstates are equal if all of their part names
        are equal and all of their cell's values return True for
        is_equal()
        """
        for (this, that) in zip(self, other):
            if this[0] != that[0]:
                # compare key names
                return False
            if not this[1].is_equal(that[1]):
                # compare cells
                return False
        return True
        
    def is_contradictory(self, other):
        """ Two beliefstates are incompatible if the other beliefstates's cells
         are not consistent with or accessible from the caller. """
        for (s_key, s_val) in self:
            if s_key in other and s_val.is_contradictory(other[s_key]):
                return True 
        return False 

    def size(self):
        """ Returns the size of context set:  *the number of referents (sets of cells) with 
        arities consistent with the beliefstate's airity constraint*.
        
        Initially, if there are $n$ targets (the result of `self.number_of_singleton_referents()`) 
        then there are $2^{n}-1$ valid belief states.
        """
        low, high = self['speaker_goals']['targetset_arity'].get_tuple()
        n = self.number_of_singleton_referents()
        if low <= 0 and high >= n:
            # no constraints on size
            return (2**n)-1
        elif low == high == 1:
            # singular
            return n
        elif low == 2 and high > n:
            # plural
            if n == 1:
                return 0
            return (2**n)-n-1
        elif low > n:
            # inconsistent
            return 0
        elif low == high:
            # single arity constraint, return nCk
            k = low
            return choose(n, k)
        else:
            message = "low=%i high=%i n=%i" % (low, high, n)
            raise Exception(message)

    def referents(self):
        """ Returns all members of the context set that are compatible with the current beliefstate.
        Warning: the number of referents is quadradic in elements of singleton referents/cells.  
        Call `size()` method instead to compute size only, without ennumerating them.
        """
        return list(self.iter_referents())
    
    def iter_referents(self):
        """ Generates members of the context set that are compatible with the current beliefstate. """
        low, high = self['speaker_goals']['targetset_arity'].get_tuple()
        min_size = max(1, low)
        max_size = min(high + 1, self.number_of_singleton_referents()+1)
        iterable = list(self.iter_singleton_referents())
        for elements in itertools.chain.from_iterable(itertools.combinations(iterable, r) \
                for r in range(min_size, max_size)):
            yield  elements

    def number_of_singleton_referents(self):
        """
        Returns the number of singleton members of the contextset (cells in domain) that are
        compatible with the current belief state.

        This is the size of the union of all referent sets.
        """
        if self.__dict__['contextset']:
            ct = 0
            for i in self.iter_singleton_referents():
                ct += 1
            return ct
        else:
            raise Exception("self.contextset must be defined")

    def iter_singleton_referents(self):
        """
        Iterator of all of the singleton members of the context set.

        NOTE: this evaluates cells one-at-a-time, and does not handle relational constraints.
        """
        try:
            for member in self.__dict__['contextset'].cells:
                if self['target'].is_entailed_by(member):
                    yield member['num'], member
        except KeyError:
            raise Exception("No contextset defined")

    def copy(self):
        """
        Copies the BeliefState by recursively deep-copying all of
        its parts.  Domains are not copied, as they do not change
        during the interpretation or generation.
        """
        copied = BeliefState(self.__dict__['contextset']) 
        for key in ['environment_variable', 'pos', 'p']:
            copied.__dict__[key] = copy.deepcopy(self.__dict__[key])
        return copied

    def __hash__(self):
        """
        This is the all-important hash method that recursively computes a hash
        value from the components of the beliefstate.  The search process treats
        two beliefstates as equal if their hash values are the same.
        """
        hashval = 0

        # hash part of speech
        hashval += hash(self.__dict__['pos'])

        # hash environment variables
        for ekey, kval in self.__dict__['environment_variable'].items():
            hashval += hash(ekey) + hash(kval)

        # hash dictionary
        for value in self.__dict__['p']:
            hashval += hash(self.__dict__['p'][value])

        # -2 is a reserved value 
        if hashval == -2:
            hashval = -1

        return hashval

    __eq__ = is_equal



