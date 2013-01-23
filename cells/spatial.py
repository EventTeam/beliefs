from .dicts import *
from .numeric import *
from .strings import *
from math import radians, cos, sin, asin, sqrt

class LatLonCell(DictCell):
    """
    Holds a Latitude and Longitude.
    
    TODO:  we should allow an address to be 'coerced' into a LatLonCell via a special 
    Geocoding operation, and then stored in 'to_addresscell'
    
    """
    def __init__(self):
        structure = {}
        structure['lat'] = IntervalCell(-90.0, 90.0)
        structure['lon'] = IntervalCell(-180.0, 180.0)
        DictCell.__init__(self, structure)
        self.to_addresscell = None  # cached addresscell pointer

    def __sub__(self, other):
        """
        Overloads the - operator to call the haversine distance
        function.
        
        Requires that the lat/lon values are scalars, not intervals,
        or it raises an exception.  (We could generalize haversine to 
        work with intervals, but I couldn't think of a usecase)
        """
        if self['lat'].low == self['lat'].high and \
                self['lon'].low == self['lon'].high and \
                other['lat'].low == other['lat'].high and \
                other['lon'].low == other['lon'].high:
            return self.haversine(other)
        else:
            raise Exception("Cannot compute distance of intervals")

    def haversine(self, other):
        """
        Calculate the great circle distance between two points
        on the earth (specified in decimal degrees)
        """
        # convert decimal degrees to radians
        lon1, lat1, lon2, lat2 = map(radians,\
                [self.lon.low, self['lat'].low, other.lon.low,
                    other['lat'].low])
        # haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2) ** 2
        c = 2 * asin(sqrt(a))
        # multiply by radius of the earth
        # km = 6367 * c
        miles = 3961 * c
        return miles

class AddressCell(DictCell):
    """
    Holds an Address
    
    TODO: coerce to LatLonCell via inverse geocoding operation
    """
    def __init__(self):
        structure = {}
        structure['street'] = StringCell()
        structure['city'] = StringCell()
        structure['state'] = StringCell()
        structure['zip'] = StringCell()
        structure['gps'] = LatLonCell()
        DictCell.__init__(self, structure)
        self.to_latlongcell = None  # cached latlon cell pointer
