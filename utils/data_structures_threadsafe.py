import math
import multiprocessing
from utils.conversion import Conversion


class Point2(object):
    def __init__(self, y=0, x=0):
        self._y = multiprocessing.Value('f', y)
        self._x = multiprocessing.Value('f', x)
        self.conversion = Conversion()

    @property
    def x(self):
        return self._x.value

    @x.setter
    def x(self, value):
        self._x.value = value

    @property
    def y(self):
        return self._y.value

    @y.setter
    def y(self, value):
        self._y.value = value

    def mm2pix(self):
        return Point2(self.conversion.mm2pix(self.y), self.conversion.mm2pix(self.x))

    def pix2mm(self):
        return Point2(self.conversion.pix2mm(self.y), self.conversion.pix2mm(self.x))

    def distance(self, other):
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def magnitude(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def get_angle_to(self, other):
        a = math.atan2(-(other.y - self.y), (other.x - self.x))
        # atan2 can return negative from the x-axis
        if a < 0:
            a += 2.0 * math.pi
        return a

    def pickle(self):
        return {
            'x': self.x,
            'y': self.y
        }

    def __str__(self):
        return 'x ' + str(self.x) + ', y ' + str(self.y)

    def __reduce__(self):
        return self.__class__, (self.y, self.x)

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
        yield self.y
        yield self.x


class Point3(object):
    def __init__(self, y=0, x=0, r=0):
        self._y = multiprocessing.Value('f', y)
        self._x = multiprocessing.Value('f', x)
        self._r = multiprocessing.Value('f', r)
        self.conversion = Conversion()

    @property
    def x(self):
        return self._x.value

    @x.setter
    def x(self, value):
        self._x.value = value

    @property
    def y(self):
        return self._y.value

    @y.setter
    def y(self, value):
        self._y.value = value

    @property
    def r(self):
        return self._r.value

    @r.setter
    def r(self, value):
        self._r.value = value

    def mm2pix(self):
        return Point3(self.conversion.mm2pix(self.y), self.conversion.mm2pix(self.x), self.r)

    def pix2mm(self):
        return Point3(self.conversion.pix2mm(self.y), self.conversion.pix2mm(self.x), self.r)

    def distance(self, other):
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def magnitude(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def get_angle_to(self, other):
        a = math.atan2(-(other.y - self.y), (other.x - self.x))
        # atan2 can return negative from the x-axis
        if a < 0:
            a += 2.0 * math.pi
        return a

    def pickle(self):
        return {
            'x': self.y,
            'y': self.x,
            'r': self.r
        }

    def __str__(self):
        return 'x ' + str(self.x) + ', y ' + str(self.y) + ', r ' + str(math.degrees(self.r))

    def __reduce__(self):
        return self.__class__, (self.y, self.x, self.r)

    def __getitem__(self, *args):
        if args[0] is None:
            return self.y, self.x, self.r
        else:
            item, = args

        if item == 0:
            return self.y
        elif item == 1:
            return self.x
        elif item == 2:
            return self.r
        else:
            raise ValueError('Invalid coordinate id')

    def __setitem__(self, *args):
        if len(args) == 3:
            self.y, self.x, self.r = args
        else:
            key, value = args
        if key == 0:
            self.y = value
        elif key == 1:
            self.x = value
        elif key == 2:
            self.r = value
        else:
            raise ValueError('Invalid coordinate id')

    def __iter__(self):
        yield self.y
        yield self.x
        yield self.r
