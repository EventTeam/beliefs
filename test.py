from beliefs.cells import *

from nose.tools import assert_raises 


# Testing new merge methods

# BoolCell tests
# x = T, y = F
x = BoolCell(T)
y = BoolCell(F)
z = BoolCell(U)

assert x == x
assert y == y
assert z == z

assert hash(x) == hash(x)
assert hash(x) != hash(y)

assert x.entails(T) == True
assert y.entails(T) == False
assert z.entails(U) == True
assert y.entails(F) == True
assert x.entails(T or F) == True
assert x.entails(U) == True
assert z.entails(F) == False #

assert x.is_entailed_by(U) == False #
assert y.is_entailed_by(F) == True
assert z.is_entailed_by(U) == True

assert x.is_contradictory(y) == y.is_contradictory(x) == True
assert z.is_contradictory(x) == z.is_contradictory(y) == z.is_contradictory(U) == False

v = BoolCell(U)
assert v.merge(T) == T
assert z.merge(F) == F


# IntervalCell tests
# x = 1, y = 2
w = IntervalCell(1,2)
x = IntervalCell(1,1)
y = IntervalCell(2,2)
z = IntervalCell(0,3)

assert x == 1
assert y == 2

assert hash(x) == hash(x)
assert hash(x) != hash(y)

assert z.is_entailed_by(x) == True
assert z.is_entailed_by(y) == True

assert w.entails(z) == True
assert x.entails(z) == True
assert y.entails(z) == True

assert x.is_contradictory(y) == True
assert w.is_contradictory(z) == False
assert x.is_contradictory(w) == False


# StringCell tests
w = StringCell("words")
x = StringCell("word")
y = StringCell("saying")
z = StringCell("phrase")

assert x == x
assert y == y
assert z == z

assert hash(x) == hash(x)
assert hash(x) != hash(y)

assert x.is_contradictory(y) == True
assert x.is_contradictory(w) == False

assert x.is_entailed_by(z) == False
assert y.is_entailed_by(z) == False

assert z.entails(x) == False
assert y.entails(z) == False
assert x.entails(x) == True

assert w.merge(x) == "words"

# ColorCell
x = RGBColorCell(0,0,0)
y = RGBColorCell.from_name('red')
z = RGBColorCell.from_name('green')

assert y == y
assert z == z

assert hash(x) == hash(x)
assert hash(x) != hash(y)

assert x.is_contradictory(y) == True
assert y.is_contradictory(x) == True

t = RGBColorCell.from_name("teal")
u = RGBColorCell.from_name("medium_blue")
v = RGBColorCell.from_name('blue')

assert t.is_contradictory(u) == True

assert v.is_entailed_by(u) == False
assert u.entails(v) == False
assert v.is_entailed_by(t) == False
assert u.entails(v) == False

assert t.is_entailed_by(u) == False
assert u.is_entailed_by(v) == False
assert t.entails(u) == False
assert u.entails(t) == False


# DictCell
v = DictCell({"name" :StringCell("name"), "color": RGBColorCell.from_name("green")})
w = DictCell({"name": StringCell("name")})
x = DictCell({"name": StringCell("name"),"size": IntervalCell(0,100), "color": RGBColorCell.from_name("red")})
y = DictCell({"name": StringCell("different_name"),"size": IntervalCell(50,75), "color": RGBColorCell.from_name("blue")})
z = DictCell({"location": StringCell("home"), "distance": IntervalCell(10,15)})

assert x == x
assert y == y
assert z == z

assert hash(x) == hash(x)
assert hash(x) != hash(y)

assert x.entails(z) == False
assert z.entails(x) == False
assert w.entails(x) == False
assert x.entails(w) == True

assert x.is_entailed_by(z) == False
assert z.is_entailed_by(x) == False
assert x.is_entailed_by(w) == False
assert w.is_entailed_by(x) == True

assert x.is_contradictory(y) == True
assert x.is_contradictory(w) == False
assert v.is_contradictory(x) == True

assert v.merge(w) == DictCell({"name":StringCell("name"), "color" : RGBColorCell(0,128,0)})
# test merges
d1 = DictCell({'a2' : {'b2' : BoolCell(F)}})
d2 = DictCell({'a2' : {'b2' : BoolCell(),
                       'b1' : BoolCell()},
               'a1' : {'b1' : {'c1' : BoolCell()}}})
d3 = DictCell({'a2' : {'b2' : BoolCell(F)}})
assert d2.merge(d1) == d3.merge(d2)
assert hash(d2.merge(d1)) == hash(d3.merge(d2))

assert_raises(Exception, lambda x: v.merge(z), "Merge fail")

assert_raises(Exception, lambda x: x.merge(y), "Merge fail")

#LinearOrderedCell
v = LinearOrderedCell(['animal','dog','poodle','toy poodle'], 'animal', 'toy poodle')
w = LinearOrderedCell(['animal','dog','poodle','toy poodle'], 'dog', "toy poodle")
x = LinearOrderedCell(['animal','dog','poodle','toy poodle'], 'animal', 'poodle')
y = LinearOrderedCell(['animal','dog','poodle','toy poodle'], 'dog', 'dog')
z = LinearOrderedCell(['animal','dog','poodle','toy poodle'], 'poodle', 'toy poodle')

assert x == x
assert y == y
assert z == z

assert hash(x) == hash(x)
assert hash(x) != hash(y)

assert v.entails(z) == False
assert z.entails(v) == True
assert w.entails(v) == True

assert z.is_entailed_by(x) == False
assert w.is_entailed_by(z) == True
assert y.is_entailed_by(x) == False
assert x.is_entailed_by(y) == True

assert w.is_contradictory(y) == y.is_contradictory(w) == False
assert y.is_contradictory(z) == True
assert z.is_contradictory(y) == True #?
assert z.is_contradictory(x) == False
assert v.is_contradictory(z) == False

u = v.merge(w)
assert u.is_equal(LinearOrderedCell(['animal', 'dog', 'poodle', 'toy poodle'], 'dog', 'toy poodle'))


# ListCell
v = ListCell(["d", "e", "f"])
w = ListCell([2,3])
x = ListCell([1,2,3])
y = ListCell(["a", "b","c"])
z = ListCell([1,2])

assert x == x
assert y == y

assert hash(x) == hash(x)
assert hash(x) != hash(y)

assert x.is_entailed_by(z) == False
assert z.is_entailed_by(x) == True

assert z.entails(x) == False
assert x.entails(z) == True

assert z.is_contradictory(w) == True
assert z.is_contradictory(x) == False

# Unlike-type tests
assert y.entails(x) == False
assert x.entails(y) == False
assert x.is_entailed_by(y) == False
assert y.is_entailed_by(x) == False
assert x.is_contradictory(y) == True
assert y.is_contradictory(x) == True

