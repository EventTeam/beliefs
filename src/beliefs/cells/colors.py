from beliefs.cells import *
from colormath.color_objects import *

COLOR_NAMES = {'red': [255,0,0],
                'cyan': [0,255,255],
                'blue': [0, 0, 255],
                'medium_blue': [0, 0, 205],
                'black': [0,0,0],
                'white': [255,255,255],
                'green': [0,128,0],
                'light_blue': [30, 144,255], #doger blue
                'teal': [0, 128, 128],
                'yellow': [255, 255,0]}

class RGBColorCell(Cell):
    """
    A Cell representation of an RGB Color.
    """

    def __init__(self, r=None, b=None, g=None):
        """ Instantiates a color of RGB """
        self.r = r
        self.b = b
        self.g = g
        self.value = None
        if not (r is None or b is None or g is None):
            self.value = RGBColor(r, b, g, rgb_type='sRGB')

    @classmethod
    def from_name(clz, name):
        """
        Instantiates the object from a known name.
        """
        if isinstance(name, list) and "green" in name:
            name = "teal"
        assert name in COLOR_NAMES, 'Unknown color name'
        r, b, g = COLOR_NAMES[name]
        return clz(r, b, g)


    def to_html(self):
        """ Converts to Hex """
        out = "#"
        if self.r == 0:
            out += "00"
        else:
            out += hex(self.r)[2:]
        if self.b == 0:
            out += "00"
        else:
            out += hex(self.b)[2:]
        if self.g == 0:
            out += "00"
        else:
            out += hex(self.g)[2:]
        return out
        
    def __hash__(self):
        """
        Representation of set color
        """
        rgb = [self.r, self.b, self.g]
        return reduce(lambda x,y: hash(x) ^ hash(y), rgb, 0)

    @classmethod
    def coerce(clz, other):
        """
        Raises an Exception if other is not an instance of RGBColorCell.

        :param other:
        :type other: RGBColorCell
        :returns: RGBColorCell
        :raises: Exception
        """
        if not isinstance(other, RGBColorCell):
            raise Exception("Needs to be another color cell")
        return other

    def membership_score(self, element):
        """
        Fuzzy set gradable membership score. 
        See http://code.google.com/p/python-colormath/wiki/ColorDifferences

        :param element: A Color Cell
        :type element: RGBColorCell
        :returns: float - In the range of 0 to 1
        :raises: Exception
        """
        other = self.coerce(element)
        if self.value and other.value:
            return 1 - (self.value.delta_e(other.value, mode='cmc', pl=1, pc=1) / 200.0)
        else:
            return 0.0

    def merge(self, other):
        """
        Merges the values
        """
        print "MERGING", self, other
        other = self.coerce(other)
        if self.is_contradictory(other):
            raise Contradiction("Cannot merge %s and %s" % (self, other))
        elif self.value is None and not other.value is None:
            self.r, self.g, self.b = other.r, other.g, other.b
            self.value = RGBColor(self.r, self.b, self.g, rgb_type='sRGB')
        # last cases: other is none, or both are none
        
        return self

    def is_contradictory(self, other):
        """
        """
        return self.value and other.value and self.membership_score(other) != 1.0

    def is_entailed_by(self, other):
        """"""
        return self.value is None or self.is_equal(other)
            
    def is_equal(self, other):
        """
        Returns True if the distance is 0
        """
        return self.membership_score(other) == 1.0


    def __repr__(self):
        import json
        if self.r is None:
            return '{}'
        else:
            return json.dumps(self.__dict__)
        
    def __str__(self):
        """
        Representation of color
        """
        if self.value:
            rgb = (self.r, self.b, self.g)
            return "[RGBColorCell:%i,%i,%i]" % rgb
        else:
            return "[RGBColorCell:X]"

    __eq__ = is_equal

# delta_e(c2, mode='cie1976')

def test_rgb_color_cell():
    r0 = RGBColorCell()
    r1 = RGBColorCell.from_name('red')
    r2 = RGBColorCell.from_name('red')
    assert not r0.is_contradictory(r1)
    assert not r1.is_contradictory(r0)
    assert r1 != r0
    print r0
    r0.merge(r1)
    print r0
    assert r0 == r1
    assert r1 == r2
    assert r1.membership_score(r2) == 1.0
    assert not r1.is_contradictory(r2)
    assert hash(r1) == hash(r2)
    g = RGBColorCell.from_name('green')
    print g.membership_score(r1)
    assert r1 != g
    assert r1.is_contradictory(g)
    g = RGBColorCell.from_name('green')
    # black and white must be very different
    b = RGBColorCell.from_name('black')
    w = RGBColorCell.from_name('white')
    assert b.membership_score(w) < 0.05
    b1 = RGBColorCell.from_name('blue')
    b2 = RGBColorCell.from_name('light_blue')
    b3 = RGBColorCell.from_name('medium_blue')
    b4 = RGBColorCell.from_name('cyan')
    b5 = RGBColorCell.from_name('teal')


if __name__ == '__main__':
    test_rgb_color_cell()
