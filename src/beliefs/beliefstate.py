from copy import copy
from collections import OrderedDict, defaultdict
from beliefs.cells import *
from belief_utils import choose
import itertools

class BeliefState(DictCell):
    """
    Represents a beliefstate, a partial information object *about* specific targets.
    A beliefstate is a continuum between individual cells and entire classes of cells.
        
    Suppose the domain has entities/cells: 1,2,3.  A beliefstate represents the
    possible groupings of these entities; a single grouping is called a *referent*. 
    A beliefstate can be about "all referents of size two", for example, and computing
    the beliefstate's extension would yield the targets {1,2}, {2,3}, and {1,3}.
    
    In addition to containing a description of the intended targets, a belief state contains information
    about the relational constraints (such as arity size), and linguistic decisions.
    """
    def __init__(self, contextset=None):
        """ 
        Initializes an empty beliefsstate, and stores the contextset (if specified) 
        into self.contextset. 
         
        By default, beliefstates are given the 'S' part of speech and an empty
        environment variable stack.
        
        Most commonly, beliefstates are created by calling the `copy()` method
        from a previous beliefstate.
        """
        self.__dict__['pos'] = 'S'  # syntactic state
        self.__dict__['contextset'] = contextset
        self.__dict__['environment_variables'] = {}
        self.__dict__['deferred_effects'] = []

        default_structure = {'target': DictCell(),
                             'distractor': DictCell(),
                             'targetset_arity': IntervalCell(),
                             'contrast_arity': IntervalCell(),
                             'is_in_commonground': BoolCell(),
                'speaker_model': {'is_syntax_stacked': BoolCell(T)}}

        DictCell.__init__(self, default_structure)

    def set_pos(self, pos):
        """ Sets the beliefstates's part of speech, `pos`, and then executes
        any deferred effects that are keyed by that pos tag.
        """
        self.__dict__['pos'] = pos
        # if any deferred effects are keyed by this pos tag, evaluate them, and
        # return their cumulative costs
        return self.execute_deferred_effects(pos)

    def get_pos(self):
        """ Returns Part of Speech"""
        return self.__dict__['pos']

    def add_deferred_effect(self, effect, pos):
        """ Pushes an (pos, effect) tuple onto a stack to later be executed if the
        state reaches the 'pos'."""
        if not isinstance(pos, (unicode, str)):
            raise Exception("Invalid POS tag. Must be string not %d" % (type(pos)))
        if self['speaker_model']['is_syntax_stacked'] == True:
            self.__dict__['deferred_effects'].insert(0,(pos, effect,))
        elif self['speaker_model']['is_syntax_stacked'] == False:
            self.__dict__['deferred_effects'].append((pos, effect,))
        else:
            raise Contradiction("Speaker Model undefined")

    def execute_deferred_effects(self, pos):
        """ Evaluates deferred effects that are triggered by the prefix of the
        pos on the current beliefstate. For instance, if the effect is triggered
        by the 'NN' pos, then the effect will be triggered by 'NN' or 'NNS'."""
        costs = 0
        to_delete = []
        for entry in self.__dict__['deferred_effects']:
            effect_pos, effect = entry
            if pos.startswith(effect_pos):
                #logging.info("Executing deferred effect" + str(effect))
                costs += effect(self)
                to_delete.append(entry)
        # we delete afterwards, because Python cannot delete from a list that
        # is being iterated over without screwing up the iteration.
        for entry in to_delete:
            self.__dict__['deferred_effects'].remove(entry)
        return costs

    def set_environment_variable(self, key, val):
        """ Sets a variable if that variable is not already set """
        if self.get_environment_variable(key) in [None, val]:
            self.__dict__['environment_variables'][key] = val
        else:
            raise Contradiction("Could not set environment variable %s" % (key))

    def get_environment_variable(self, key, default=None, pop=False):
        if key in self.__dict__['environment_variables']:
            val = self.__dict__['environment_variables'][key]
            if pop:
                del self.__dict__['environment_variables'][key]
            return val
        else:
            return default

    def has_contextset(self):
        """
        Returns True if the BeliefState has a context set defined -- meaning a 
        list of external referents.
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


    def get_nth_unique_value(self, keypath, n, distance_from, open_interval=True):
        """
        Returns the `n-1`th unique value, or raises
        a contradiction if that is out of bounds
        """
        unique_values = self.get_ordered_values(keypath, distance_from, open_interval)
        if 0 <= n < len(unique_values):
            #logging.error("%i th unique value is %s" % (n, str(unique_values[n])))
            return unique_values[n]
        else:
            raise Contradiction("n-th Unique value out of range: " + str(n))

    def get_ordered_values(self, keypath, distance_from, open_interval=True):
        """
        Retrieves the referents's values sorted by their distance from the
        min, max, or mid value.
        """

        values = []
        if keypath[0] == 'target':
            # instances start with 'target' prefix, but 
            # don't contain it, so we remove it here.
            keypath = keypath[1:]
        for _, instance in self.iter_singleton_referents():
            value = instance.get_value_from_path(keypath)
            if hasattr(value, 'low') and value.low != value.high:
                return []
            values.append(float(value))

        if len(values) == 0:
            return []
        values = np.array(values)
        anchor = values.min()
        diffs = values - anchor
        if distance_from == 'max':
            anchor = values.max()
            diffs = anchor - values
        if distance_from == 'mean':
            anchor = values.mean()
            diffs = abs(anchor - values)

        sdiffs = np.unique(diffs)
        sdiffs.sort()
        results = []
      
        for ix, el in enumerate(sdiffs):
            mask = diffs <= el
            vals = values[mask]
            if False:
                # when vagueness has been made precise through an ordinal
                results.append(IntervalCell(vals.min(), vals.max()))
            elif distance_from == 'max':
                if open_interval:
                    results.append(IntervalCell(vals.min(), np.inf))
                else:
                    results.append(IntervalCell(vals.min(), vals.min()))
            elif distance_from == 'min':
                if open_interval:
                    results.append(IntervalCell(-np.inf, vals.max()))
                else:
                    results.append(IntervalCell(vals.max(), vals.max()))
            elif distance_from == 'mean':
                if ix+1 == len(sdiffs): continue  # skip last
                results.append(IntervalCell(vals.min(), vals.max()))
        return results 

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
        Returns a path list to all attributes that have with a particular name.
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
        negated = False
        keypath = keypath[:] # copy it 
        if keypath[0] == 'target':
            # only pull negated if it can potentially modify target
            negated = self.get_environment_variable('negated', pop=True, default=False)
            if negated:
                keypath[0] = "distractor"

        if keypath not in self:
            first_referent = None
            if keypath[0] in ['target', 'distractor']:
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
                        raise CellConstructionFailure("Cannot merge; no target: %s" \
                            % (str(keypath)))
                    else:
                        # this will always happen when size is 0
                        raise CellConstructionFailure("Empty belief state")
                # find the type and add it to the 
                cell = first_referent.get_value_from_path(keypath[1:]).stem()
                self.add_cell(keypath, cell)
            else:
                # should we allow merging undefined components outside of target?
                raise Exception("Could not find Keypath %s" % (str(keypath)))

        # break down keypaths into 
        cell = self
        if not isinstance(keypath, list):
            keypath = [keypath]
        for key in keypath:
            cell = cell[key]
        # perform operation (set, <=, >= etc)
        try:
            return getattr(cell, op)(value)
        except Contradiction as ctrd:
            # add more information to the contradiction
            raise Contradiction("Could not merge %s with %s: %s " % (str(keypath), str(value), ctrd))
   
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
        One beliefstate entails another beliefstate iff the other state's cells are
        all equal or more general than the caller's parts.  That means the other 
        state must have at least all of the same keys/components.  

        Note: this only compares the items in the DictCell, not `pos`,
        `environment_variables` or `deferred_effects`.
        """
        return other.is_entailed_by(self)

    def is_entailed_by(self, other):
        """
        Given two beliefstates, returns True iff the calling instance
        implies the other beliefstate, meaning it contains at least the same
        structure (for all structures) and all values (for all defined values).
        
        Inverse of `entails`.

        Note: this only compares the items in the DictCell, not `pos`,
        `environment_variables` or `deferred_effects`.
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
        Two beliefstates are equal if all of their part names are equal and all
        of their cell's values return True for is_equal().

        Note: this only compares the items in the DictCell, not `pos`,
        `environment_variables` or `deferred_effects`.
        """
        return hash(self) == hash(other)
        for (this, that) in itertools.izip_longest(self, other):
            if that[0] is None or this[0] != that[0]:
                # compare key names
                return False
            if not this[1].is_equal(that[1]):
                # compare cells
                return False
        return True
        
    def is_contradictory(self, other):
        """ Two beliefstates are incompatible if the other beliefstates's cells
         are not consistent with or accessible from the caller.
         
        Note: this only compares the items in the DictCell, not `pos`,
        `environment_variables` or `deferred_effects`.
        """
        for (s_key, s_val) in self:
            if s_key in other and s_val.is_contradictory(other[s_key]):
                return True 
        return False 

    def size(self):
        """ Returns the size of the belief state.

        Initially if there are $n$ consistent members, (the result of `self.number_of_singleton_referents()`) 
        then there are generally $2^{n}-1$ valid belief states.
        """
        n = self.number_of_singleton_referents()
        targets = list(self.iter_referents_tuples())
        n_targets = len(targets)
        if n == 0 or n_targets == 0:
            return  0

        if len(self.__dict__['deferred_effects']) != 0:
            return -1 

        tlow, thigh = self['targetset_arity'].get_tuple()
        clow, chigh = self['contrast_arity'].get_tuple()
        
        return binomial_range(n, max(tlow,1), min([n-max(clow,0),thigh,n]))

    def referents(self):
        """ Returns all target sets that are compatible with the current beliefstate.
        Warning: the number of referents can be quadradic in elements of singleton referents/cells.  
        Call `size()` method instead to compute size only, without enumerating them.
        """
        # all groupings of singletons
        return list(self.iter_referents())
    
    def iter_referents(self):
        """ Generates target sets that are compatible with the current beliefstate. """
        tlow, thigh = self['targetset_arity'].get_tuple()
        clow, chigh = self['contrast_arity'].get_tuple()

        referents = list(self.iter_singleton_referents())
        t = len(referents)
        low = max(1, tlow)
        high = min([t,  thigh])

        for targets in itertools.chain.from_iterable(itertools.combinations(referents, r) \
            for r in reversed(xrange(low, high+1))):
            if clow <= t-len(targets) <= chigh:
                yield  targets

    def iter_referents_tuples(self):
        """ Generates target sets (as tuples of indicies) that are compatible with
        the current beliefstate."""
        tlow, thigh = self['targetset_arity'].get_tuple()
        clow, chigh = self['contrast_arity'].get_tuple()
        singletons = list([int(i) for i,_ in self.iter_singleton_referents()])
        t = len(singletons)
        low = max(1, tlow)
        high = min([t,  thigh])
        #if low == 2: min_size = max_size-1 # weird hack
        for elements in itertools.chain.from_iterable(itertools.combinations(singletons, r) \
                for r in reversed(xrange(low, high+1))):
            if clow <= t-len(elements) <= chigh:
                yield  elements

    def number_of_singleton_referents(self):
        """
        Returns the number of singleton members of the referring domain (cells) that are
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
                if self['target'].is_entailed_by(member) and (self['distractor'].empty() or not self['distractor'].is_entailed_by(member)):
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
        for key in ['environment_variables', 'deferred_effects', 'pos', 'p']:
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
        for ekey, kval in self.__dict__['environment_variables'].items():
            hashval += hash(ekey) + hash(kval)

        for effect in self.__dict__['deferred_effects']:
            hashval += hash(effect)

        # hash dictionary
        for key, value in self.__dict__['p'].items():
            hashval += hash(value) * hash(key)

        # -2 is a reserved value 
        if hashval == -2:
            hashval = -1

        return hashval

    __eq__ = is_equal


