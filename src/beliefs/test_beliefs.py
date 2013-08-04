from models import *
#from models.offline import *
from lexica.shapes.shape_contextset import *

from belief_utils import *

def binomial_range(n, k_low, k_high):
    if k_low > k_high: return 0
    return sum([choose(n, i) for i in range(k_low, k_high+1)])

sc = ShapeContextSet({"display_prices": False,
    "cells": [{"color": "yellow", "shape": "triangle", "num": 0, "size": 70},
              {"color": "green", "shape": "triangle", "num": 1, "size": 62},
              {"color": "green", "shape": "triangle", "num": 2, "size": 60},
              {"color": "yellow", "shape": "circle", "num": 3, "size": 80}], "size": 4})

def plural_constraint(belief):
    belief.merge(['targetset_arity'], 2, '__ge__')

def singular_constraint(belief):
    belief.merge(['targetset_arity'], 1)

def yellow(belief):
    belief.merge(['target', 'color'], 'yellow')

def has_distractors(belief):
    belief.merge(['contrast_arity'], 1, '__ge__')

def negate(belief):
    belief.set_environment_variable('negated', True)

new_beliefstate = sc.get_beliefstate_constructor()

els = len(sc.cells)
print "Initial belief state with %i elements " % (len(sc.cells))
b = new_beliefstate()
assert len(b.referents()) == b.size() == len(list(b.iter_referents_tuples())) == 2**els-1
print "Size of belief state %i" % (b.size()) # 7
t  = b.number_of_singleton_referents()
tlow, thigh = b['targetset_arity'].get_tuple()
dlow, dhigh = b['contrast_arity'].get_tuple()
print binomial_range(t, max(tlow,1), min([t-max(dlow,0),thigh,t]))


print "\n\nAdding Plural Constraint"
assert len(b.referents()) == b.size() == len(list(b.iter_referents_tuples()))
b = new_beliefstate()
plural_constraint(b)
print "Size of belief state %i" % (b.size()) # 4
t  = b.number_of_singleton_referents()
tlow, thigh = b['targetset_arity'].get_tuple()
dlow, dhigh = b['contrast_arity'].get_tuple()
print binomial_range(t, max(tlow,1), min([t-max(dlow,0),thigh,t]))
assert len(b.referents()) == b.size() == len(list(b.iter_referents_tuples()))

print "\n\nAdding Singular Constraint"
b = new_beliefstate()
singular_constraint(b)
print list(b.iter_referents_tuples())
print list(b.iter_referents_tuples())
print "Size of belief state %i" % (b.size())
t  = b.number_of_singleton_referents()
tlow, thigh = b['targetset_arity'].get_tuple()
dlow, dhigh = b['contrast_arity'].get_tuple()
print binomial_range(t, max(tlow,1), min([t-max(dlow,0),thigh,t]))
assert len(b.referents()) == b.size() == len(list(b.iter_referents_tuples()))

print "\n\nAdding Multiple Distractors"
b = new_beliefstate()
has_distractors(b)
print list(b.iter_referents_tuples())
print "Size of belief state %i" % (b.size()) # 10
t  = b.number_of_singleton_referents()
tlow, thigh = b['targetset_arity'].get_tuple()
dlow, dhigh = b['contrast_arity'].get_tuple()
print binomial_range(t, max(tlow,1), min([t-max(dlow,0),thigh,t]))
assert len(b.referents()) == b.size() == len(list(b.iter_referents_tuples()))


print "\n\nAdding Multiple Distractor requirement & Plural"
b = new_beliefstate()
has_distractors(b)
plural_constraint(b)
print list(b.iter_referents_tuples())
print "Size of belief state %i" % (b.size())  # 6
t  = b.number_of_singleton_referents()
tlow, thigh = b['targetset_arity'].get_tuple()
dlow, dhigh = b['contrast_arity'].get_tuple()
print binomial_range(t, max(tlow,1), min([t-max(dlow,0),thigh,t]))
assert len(b.referents()) == b.size() == len(list(b.iter_referents_tuples()))

print "\n\nAdding Multiple Distractor requirement & Yellow"
b = new_beliefstate()
yellow(b)
print list(b.iter_referents_tuples())
has_distractors(b)
print list(b.iter_referents_tuples())
print "Size of belief state %i" % (b.size())  # 6
t  = b.number_of_singleton_referents()
tlow, thigh = b['targetset_arity'].get_tuple()
dlow, dhigh = b['contrast_arity'].get_tuple()
print "DLOW", dlow, t-dlow
print binomial_range(t, max(tlow,1), min([t-max(dlow,0),thigh,t]))
assert len(b.referents()) == b.size() == len(list(b.iter_referents_tuples()))

""" test negated version of b."""
b2 = new_beliefstate()
negate(b2)
yellow(b2)
has_distractors(b2)
assert hash(b2) != hash(b)


b = new_beliefstate()
print b.get_ordered_values('num', 'mean')
print b.get_ordered_values('size', 'min')
print b.get_ordered_values('size', 'max')
