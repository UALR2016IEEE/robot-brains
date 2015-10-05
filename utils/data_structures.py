__author__ = 'StaticVOiDance'


class Point:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __getitem__(self, item):
        if item == 0:
            return self.x
        elif item == 1:
            return  self.y
        else:
            raise ValueError('Invalid coordinate id')

    def __setitem__(self, key, value):
        if key == 0:
            self.x = value
        elif key == 1:
            self.y = value
        else:
            raise ValueError('Invalid coordinate id')

    def __iter__(self):
        yield self.x
        yield self.y

