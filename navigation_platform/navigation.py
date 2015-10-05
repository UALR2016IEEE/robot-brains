import types

__author__ = 'StaticVOiDance'

from utils import Point


class _BaseNavigation:
    def __init__(self, cid: str=None):
        self.components = {}

    def get_pos(self) -> Point:
        point = Point()
        return point

    @property
    def position(self):
        return self.get_pos()

    def set_pos(self, point: Point):
        pass

    def add_component(self, name: str, func: types.FunctionType):
        self.components[name] = func()

    def run_components(self, lidar_data):
        for key, component in self.components.items():
            if component.send(lidar_data):
                self.components.pop(key)


class Navigation(_Base):
    def __init__(self, cid: str=None):
        if cid:
            self.connect(cid)

    def connect(self, cid: str=None):
        pass
