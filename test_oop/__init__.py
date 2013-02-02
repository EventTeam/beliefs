from test_oop import *
from beliefs.referent import *
import sys

TaxonomyCell.initialize(sys.modules[__name__])
m = MusicalThing()
print m
t = TaxonomyCell()
t.to_dot()

