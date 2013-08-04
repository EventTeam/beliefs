#-----------------------------------------------------------------------------------------------------------------
# Utility functions used by NLPlanner
#-----------------------------------------------------------------------------------------------------------------
import re
from itertools import *
from collections import OrderedDict, Callable

class DefaultOrderedDict(OrderedDict):
    # from http://stackoverflow.com/questions/6190331/can-i-do-an-ordered-default-dict-in-python
    def __init__(self, default_factory=None, *a, **kw):
        if (default_factory is not None and
            not isinstance(default_factory, Callable)):
            raise TypeError('first argument must be callable')
        OrderedDict.__init__(self, *a, **kw)
        self.default_factory = default_factory

    def __getitem__(self, key):
        try:
            return OrderedDict.__getitem__(self, key)
        except KeyError:
            return self.__missing__(key)

    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        self[key] = value = self.default_factory()
        return value

    def __reduce__(self):
        if self.default_factory is None:
            args = tuple()
        else:
            args = self.default_factory,
        return type(self), args, None, None, self.items()

    def copy(self):
        return self.__copy__()

    def __copy__(self):
        return type(self)(self.default_factory, self)

    def __deepcopy__(self, memo):
        import copy
        return type(self)(self.default_factory,
                          copy.deepcopy(self.items()))
    def __repr__(self):
        return 'OrderedDefaultDict(%s, %s)' % (self.default_factory,
                                        OrderedDict.__repr__(self))

def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

def flatten_list(l):
    """ Nested lists to single-level list, does not split strings"""
    return list(chain.from_iterable(repeat(x,1) if isinstance(x,str) else x for x in l))

def list_diff(list1, list2):
    """ Ssymetric list difference """
    diff_list = []
    for item in list1:
        if not item in list2:
            diff_list.append(item)
    for item in list2:
        if not item in list1:
            diff_list.append(item)
    return diff_list

def asym_list_diff(list1, list2):
    """ Asymmetric list difference """
    diff_list = []
    for item in list1:
        if not item in list2:
            diff_list.append(item)
    return diff_list

def is_alphanumeric(strg, search=re.compile(r'[^a-z0-9 ]').search):
    return not bool(search(strg))

def is_number(var):
    """
    Returns True if variable is an integer, long, float or complex data
    type, and False otherwise.
    """
    return isinstance(var, (int, long, float, complex))

def all_words_in(source_word_list, word_list):
    """
    Ensures that all words in source are in target (not visa versa)

       all_words_in(['a'], ['another', 'day']) ==> False

       all_words_in('the boy cried'.split(),
                    'the boy cried wolf'.split()) ==> True
    """
    return asym_list_diff(source_word_list, word_list) == 0

        
def si_prefix(value):
    """ By Forrest Green (2010)"""
    #standard si prefixes
    prefixes = ['y','z','a','f','p','n','u','m','','k','M','G','T','P','E','Z','Y']

    from math import log
    #closest 1000 exponent
    if value == 0: return (value, "")
    exp = int(log(value,1000)//1) + 8
    if exp < 0: exp = 0
    if exp > 16: exp = 16
    return (value*1000**(-(exp-8)), prefixes[exp])

def get_average(items):
    return sum(items)/len(items)

def get_var(items):
    avg = get_average(items)
    return sum(map(lambda x: (x-average)**2, items))/len(items)

def stddv(items):
    return get_var(items)**0.5

def levenshtein_distance(a,b):
    "Calculates the Levenshtein distance between a and b."
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a,b = b,a
        n,m = m,n

    current = range(n+1)
    for i in range(1,m+1):
        previous, current = current, [i]+[0]*n
        for j in range(1,n+1):
            add, delete = previous[j]+1, current[j-1]+1
            change = previous[j-1]
            if a[j-1] != b[i-1]:
                change = change + 2
            current[j] = min(add, delete, change)

    return current[n]
    
def levenshtein_distance_metric(a, b):
    """ 1 - farthest apart (same number of words, all diff). 0 - same"""
    return (levenshtein_distance(a, b) / (2.0 * max(len(a), len(b), 1)))


def next_tokens_in_sequence(observed, current):
    """ Given the observed list of tokens, and the current list,
    finds out what should be next next emitted word
    """
    idx = 0
    for word in current:
        if observed[idx:].count(word) != 0:
            found_pos = observed.index(word, idx)
            idx = max(idx + 1, found_pos)
        # otherwise, don't increment idx
    if idx < len(observed):
        return observed[idx:]
    else:
        return []

def factorial(n, start=1):
    result = 1
    assert start <= n
    for i in xrange(start, abs(n)+1):
        result *= i
    if n >= 0:
        return result
    else:
        return -result

def choose(n, k):
    """
    A fast way to calculate binomial coefficients by Andrew Dalke (contrib).
    """
    if 0 <= k <= n:
        ntok = 1
        ktok = 1
        for t in xrange(1, min(k, n - k) + 1):
            ntok *= n
            ktok *= t
            n -= 1
        return ntok // ktok
    else:
        return 0

def binomial_range(n, k_low, k_high):
    if k_low > k_high: return 0
    return sum([choose(n, i) for i in range(k_low, k_high+1)])

def test_next_word():
    s1 = "the blue home".split()
    s2 = "the home home again".split()
    s3 = "the home home".split()
    s4 = "the home home".split()
    s5 = "the home sweet home".split()
    assert next_tokens_in_sequence(s1, s2) == [] 
    assert next_tokens_in_sequence(s1, s1) == [] 
    assert next_tokens_in_sequence(s2, s3) == ["again"]
    assert next_tokens_in_sequence(s2, s5) == ["again"]
    assert next_tokens_in_sequence(s3, s4) == [] 
    assert next_tokens_in_sequence(s3, ["the"]) == ['home', 'home']


if __name__ == '__main__':
    test_next_word()
    print levenshtein_distance_metric("the blue car".split(), "the car".split()) # => 0.1666
    print levenshtein_distance_metric("the blue car".split(), "the blue".split()) # => 0.1666
    test_next_word()
