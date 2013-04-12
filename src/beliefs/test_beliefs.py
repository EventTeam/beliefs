from models import *
from models.offline import *
from lexica.shapes.shape_contextset import *

from belief_utils import *

def binomial_range(n, k_low, k_high):
    if k_low > k_high: return 0
    return sum([choose(n, i) for i in range(k_low, k_high+1)])

sc = ShapeContextSet({"display_prices": False,
    "cells": [{"color": "yellow", "shape": "triangle", "num": 0, "size": 70},
              {"color": "green", "shape": "triangle", "num": 1, "size": 60},
              {"color": "yellow", "shape": "circle", "num": 3, "size": 70}], "size": 4})

def plural_constraint(belief):
    belief.merge(['speaker_goals', 'targetset_arity'], 2, '__ge__')

def singular_constraint(belief):
    belief.merge(['speaker_goals', 'targetset_arity'], 1)

def yellow(belief):
    belief.merge(['target', 'color'], 'yellow')

def has_distractors(belief):
    belief.merge(['speaker_goals', 'distractors_arity'], 1, '__ge__')

new_beliefstate = sc.get_beliefstate_constructor()

els = len(sc.cells)
print "Initial belief state with %i elements " % (len(sc.cells))
b = new_beliefstate()
assert len(b.referents()) == b.size() == len(list(b.iter_referents_tuples())) == 2**els-1
print "Size of belief state %i" % (b.size()) # 7
t  = b.number_of_singleton_referents()
tlow, thigh = b['speaker_goals']['targetset_arity'].get_tuple()
dlow, dhigh = b['speaker_goals']['distractors_arity'].get_tuple()
print binomial_range(t, max(tlow,1), min([t-max(dlow,0),thigh,t]))


print "\n\nAdding Plural Constraint"
assert len(b.referents()) == b.size() == len(list(b.iter_referents_tuples()))
b = new_beliefstate()
plural_constraint(b)
print "Size of belief state %i" % (b.size()) # 4
t  = b.number_of_singleton_referents()
tlow, thigh = b['speaker_goals']['targetset_arity'].get_tuple()
dlow, dhigh = b['speaker_goals']['distractors_arity'].get_tuple()
print binomial_range(t, max(tlow,1), min([t-max(dlow,0),thigh,t]))
assert len(b.referents()) == b.size() == len(list(b.iter_referents_tuples()))

print "\n\nAdding Singular Constraint"
b = new_beliefstate()
singular_constraint(b)
print list(b.iter_referents_tuples())
print list(b.iter_referents_tuples())
print "Size of belief state %i" % (b.size())
t  = b.number_of_singleton_referents()
tlow, thigh = b['speaker_goals']['targetset_arity'].get_tuple()
dlow, dhigh = b['speaker_goals']['distractors_arity'].get_tuple()
print binomial_range(t, max(tlow,1), min([t-max(dlow,0),thigh,t]))
assert len(b.referents()) == b.size() == len(list(b.iter_referents_tuples()))

print "\n\nAdding Multiple Distractors"
b = new_beliefstate()
has_distractors(b)
print list(b.iter_referents_tuples())
print "Size of belief state %i" % (b.size()) # 10
t  = b.number_of_singleton_referents()
tlow, thigh = b['speaker_goals']['targetset_arity'].get_tuple()
dlow, dhigh = b['speaker_goals']['distractors_arity'].get_tuple()
print binomial_range(t, max(tlow,1), min([t-max(dlow,0),thigh,t]))
assert len(b.referents()) == b.size() == len(list(b.iter_referents_tuples()))


print "\n\nAdding Multiple Distractor requirement & Plural"
b = new_beliefstate()
has_distractors(b)
plural_constraint(b)
print list(b.iter_referents_tuples())
print "Size of belief state %i" % (b.size())  # 6
t  = b.number_of_singleton_referents()
tlow, thigh = b['speaker_goals']['targetset_arity'].get_tuple()
dlow, dhigh = b['speaker_goals']['distractors_arity'].get_tuple()
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
tlow, thigh = b['speaker_goals']['targetset_arity'].get_tuple()
dlow, dhigh = b['speaker_goals']['distractors_arity'].get_tuple()
print "DLOW", dlow, t-dlow
print binomial_range(t, max(tlow,1), min([t-max(dlow,0),thigh,t]))
assert len(b.referents()) == b.size() == len(list(b.iter_referents_tuples()))

