__author__ = 'StaticVOiDance'

from utils import Point


class _Base:
    def __init__(self, cid: str=None):
        pass

    def get_pos(self) -> Point:
        point = Point()
        return point

    @property
    def position(self):
        return self.get_pos()

    def set_pos(self, point: Point):
        pass

