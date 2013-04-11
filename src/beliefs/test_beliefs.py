from models import *
from models.offline import *
from lexica.shapes.shape_contextset import *
sc = ShapeContextSet({"display_prices": False,
    "cells": [{"color": "yellow", "shape": "triangle", "num": 0, "size": 70},
              {"color": "green", "shape": "triangle", "num": 1, "size": 60},
              {"color": "yellow", "shape": "circle", "num": 2, "size": 70}], "size": 3})

def plural_constraint(belief):
    belief.merge(['speaker_goals', 'targetset_arity'], 2, '__ge__')

def singular_constraint(belief):
    belief.merge(['speaker_goals', 'targetset_arity'], 1)

def multiple_distractors(belief):
    belief.merge(['speaker_goals', 'distractors_arity'], 2, '__ge__')

new_beliefstate = sc.get_beliefstate_constructor()

b = new_beliefstate()
print "Size of belief state %i" % (b.size()) # 7
assert len(b.referents()) == b.size() == len(list(b.iter_referents_tuples()))
b = new_beliefstate()
plural_constraint(b)
print "Size of belief state %i" % (b.size()) # 4
assert len(b.referents()) == b.size() == len(list(b.iter_referents_tuples()))

print list(b.iter_referents_tuples())
b = new_beliefstate()
singular_constraint(b)
assert len(b.referents()) == b.size() == len(list(b.iter_referents_tuples()))
print "Size of belief state %i" % (b.size())
print "Num of", b.number_of_singleton_referents()
print "Size", b.size()
assert len(b.referents()) == b.size() == len(list(b.iter_referents_tuples()))


