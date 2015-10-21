import math


class Point2:
    def __init__(self, y=0, x=0):
        self._y = y
        self._x = x

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = value

    def distance(self, other):
        return math.sqrt((self.x - other.x) * (self.x - other.x) + (self.y - other.y) * (self.y - other.y))

    def pickle(self):
        return {
            'x': self.x,
            'y': self.y
        }

    def __getitem__(self, item):
        if item == 0:
            return self.y
        elif item == 1:
            return self.x
        else:
            raise ValueError('Invalid coordinate id')

    def __setitem__(self, key, value):
        if key == 0:
            self.y = value
        elif key == 1:
            self.x = value
        else:
            raise ValueError('Invalid coordinate id')

    def __iter__(self):
        yield self.x
        yield self.y


class Point3:
    def __init__(self, y=0, x=0, r=0):
        self._y = y
        self._x = x
        self._r = r

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = value

    @property
    def r(self):
        return self._r

    @r.setter
    def r(self, value):
        self._r = value

    def distance(self, other):
        return math.sqrt((self.x - other.x) * (self.x - other.x) + (self.y - other.y) * (self.y - other.y))

    def pickle(self):
        return {
            'x': self.x,
            'y': self.y,
            'r': self.r
        }

    def __getitem__(self, item):
        if item == 0:
            return self.y
        elif item == 1:
            return self.x
        elif item == 2:
            return self.r
        else:
            raise ValueError('Invalid coordinate id')

    def __setitem__(self, key, value):
        if key == 0:
            self.y = value
        elif key == 1:
            self.x = value
        elif key == 2:
            self.r = value
        else:
            raise ValueError('Invalid coordinate id')

    def __iter__(self):
        yield self.x
        yield self.y
        yield self.r
